"""Secure, provider-neutral HTTP/JSON connectors for live travel data."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Literal, Protocol, cast
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

ConnectorDomain = Literal["flights", "hotels", "transit", "activities", "weather"]
AuthMode = Literal["none", "bearer_env", "header_env", "query_env"]


class ConnectorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    provider: str = Field(min_length=1)
    domain: ConnectorDomain
    base_url: HttpUrl
    auth_mode: AuthMode = "none"
    credential_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    auth_header: str = "X-API-Key"
    auth_query_parameter: str = "key"
    allowed_path_prefix: str = "/"
    timeout_seconds: int = Field(default=20, ge=1, le=60)
    maximum_response_bytes: int = Field(default=2_000_000, ge=1024, le=10_000_000)

    @model_validator(mode="after")
    def secure_configuration(self) -> "ConnectorConfig":
        parsed = urlparse(str(self.base_url))
        if parsed.scheme != "https":
            raise ValueError("live connector base_url must use HTTPS")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url cannot contain credentials, query, or fragment")
        if self.auth_mode != "none" and not self.credential_env:
            raise ValueError("authenticated connectors require credential_env")
        if self.auth_mode == "none" and self.credential_env:
            raise ValueError("credential_env is unused when auth_mode is none")
        if not self.allowed_path_prefix.startswith("/") or (
            self.allowed_path_prefix != "/" and not self.allowed_path_prefix.endswith("/")
        ):
            raise ValueError("allowed_path_prefix must be / or an absolute directory prefix")
        return self


class ConnectorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    path: str = Field(min_length=1)
    method: Literal["GET", "POST"] = "GET"
    query: dict[str, str | int | bool] = Field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    headers: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def safe_request(self) -> "ConnectorRequest":
        if not self.path.startswith("/") or ".." in self.path.split("/"):
            raise ValueError("connector path must be absolute and cannot traverse directories")
        if self.method == "GET" and self.json_body is not None:
            raise ValueError("GET connector requests cannot contain json_body")
        forbidden = {"authorization", "proxy-authorization", "cookie"}
        if any(
            name.lower() in forbidden
            or any(marker in name.lower() for marker in ("token", "secret", "password", "key"))
            for name in self.headers
        ):
            raise ValueError("secrets must come from connector environment configuration")
        sensitive_markers = (
            "passport",
            "payment",
            "card_number",
            "security_code",
            "cvv",
            "password",
            "birth_date",
            "date_of_birth",
        )
        supplied_keys = {key.lower() for key in self.query}
        if self.json_body is not None:
            stack: list[object] = [self.json_body]
            while stack:
                value = stack.pop()
                if isinstance(value, dict):
                    supplied_keys.update(str(key).lower() for key in value)
                    stack.extend(value.values())
                elif isinstance(value, list):
                    stack.extend(value)
        if any(marker in key for key in supplied_keys for marker in sensitive_markers):
            raise ValueError("connector requests cannot contain identity or payment fields")
        return self


class ConnectorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str
    request_id: str
    provider: str
    domain: ConnectorDomain
    source_url: HttpUrl
    retrieved_at: datetime
    status_code: int
    payload: dict[str, Any] | list[Any]


class ConnectorFieldMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_field: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    source_path: str = Field(min_length=1)
    data_type: Literal["string", "integer", "decimal", "boolean"]
    required: bool = True


class ConnectorNormalizationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_path: str = ""
    mappings: list[ConnectorFieldMapping] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_targets(self) -> "ConnectorNormalizationSpec":
        targets = [mapping.target_field for mapping in self.mappings]
        if len(targets) != len(set(targets)):
            raise ValueError("normalization target fields must be unique")
        return self


class NormalizedConnectorResult(BaseModel):
    connector_id: str
    request_id: str
    provider: str
    domain: ConnectorDomain
    source_url: HttpUrl
    retrieved_at: datetime
    records: list[dict[str, str | int | Decimal | bool | None]]
    issues: list[str]
    complete: bool


class HttpResponse(Protocol):
    status: int

    def read(self, amount: int = -1) -> bytes: ...

    def geturl(self) -> str: ...

    def __enter__(self) -> "HttpResponse": ...

    def __exit__(self, *args: object) -> None: ...


OpenUrl = Callable[[Request, int], HttpResponse]


def _same_host(first: str, second: str) -> bool:
    return (urlparse(first).hostname or "").lower() == (
        urlparse(second).hostname or ""
    ).lower()


def _build_url(config: ConnectorConfig, request: ConnectorRequest, secret: str | None) -> str:
    if not request.path.startswith(config.allowed_path_prefix):
        raise ValueError("request path is outside allowed_path_prefix")
    base = str(config.base_url)
    url = urljoin(base if base.endswith("/") else f"{base}/", request.path.lstrip("/"))
    if not _same_host(base, url):
        raise ValueError("connector request cannot change host")
    parsed = urlparse(url)
    query = list(parse_qsl(parsed.query, keep_blank_values=True))
    query.extend((key, str(value).lower() if isinstance(value, bool) else str(value)) for key, value in request.query.items())
    if config.auth_mode == "query_env" and secret is not None:
        query.append((config.auth_query_parameter, secret))
    return urlunparse(parsed._replace(query=urlencode(query)))


def _redact_source_url(config: ConnectorConfig, url: str) -> str:
    if config.auth_mode != "query_env":
        return url
    parsed = urlparse(url)
    safe_query = [
        pair
        for pair in parse_qsl(parsed.query, keep_blank_values=True)
        if pair[0] != config.auth_query_parameter
    ]
    return urlunparse(parsed._replace(query=urlencode(safe_query)))


def execute_json_connector(
    config: ConnectorConfig,
    request: ConnectorRequest,
    *,
    environment: Mapping[str, str] | None = None,
    open_url: OpenUrl | None = None,
) -> ConnectorResult:
    """Execute one bounded JSON request; credentials never enter the result."""

    env = environment if environment is not None else os.environ
    secret = env.get(config.credential_env, "") if config.credential_env else None
    if config.auth_mode != "none" and not secret:
        raise ValueError(f"missing connector credential environment variable: {config.credential_env}")
    url = _build_url(config, request, secret)
    headers = {"Accept": "application/json", "User-Agent": "ultimate-travel-agent/1"}
    headers.update(request.headers)
    if config.auth_mode == "bearer_env" and secret is not None:
        headers["Authorization"] = f"Bearer {secret}"
    elif config.auth_mode == "header_env" and secret is not None:
        headers[config.auth_header] = secret
    body = None
    if request.json_body is not None:
        body = json.dumps(request.json_body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    http_request = Request(url, data=body, headers=headers, method=request.method)
    opener = open_url or cast(OpenUrl, urlopen)
    with opener(http_request, config.timeout_seconds) as response:
        final_url = response.geturl()
        if not _same_host(str(config.base_url), final_url):
            raise ValueError("connector redirect changed host")
        if not 200 <= response.status < 300:
            raise ValueError(f"connector returned HTTP status {response.status}")
        raw = response.read(config.maximum_response_bytes + 1)
        if len(raw) > config.maximum_response_bytes:
            raise ValueError("connector response exceeds maximum_response_bytes")
        try:
            payload = json.loads(raw.decode("utf-8"), parse_float=Decimal)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("connector response is not valid UTF-8 JSON") from exc
        if not isinstance(payload, (dict, list)):
            raise ValueError("connector JSON payload must be an object or array")
        return ConnectorResult(
            connector_id=config.connector_id,
            request_id=request.request_id,
            provider=config.provider,
            domain=config.domain,
            source_url=cast(HttpUrl, _redact_source_url(config, final_url)),
            retrieved_at=datetime.now(timezone.utc),
            status_code=response.status,
            payload=payload,
        )


def _read_path(value: object, path: str) -> object:
    current = value
    if not path:
        return current
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def _normalize_value(value: object, data_type: str) -> str | int | Decimal | bool:
    if data_type == "string":
        if not isinstance(value, str):
            raise ValueError("expected string")
        return value
    if data_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("expected integer")
        return value
    if data_type == "boolean":
        if not isinstance(value, bool):
            raise ValueError("expected boolean")
        return value
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError("expected exact decimal string, integer, or Decimal")
    try:
        return Decimal(value) if isinstance(value, (str, int, Decimal)) else Decimal("")
    except InvalidOperation as exc:
        raise ValueError("expected decimal") from exc


def normalize_connector_result(
    result: ConnectorResult, spec: ConnectorNormalizationSpec
) -> NormalizedConnectorResult:
    """Map a provider payload to stable records using declarative dotted paths."""

    try:
        raw_records = _read_path(result.payload, spec.record_path)
    except KeyError:
        return NormalizedConnectorResult(
            connector_id=result.connector_id,
            request_id=result.request_id,
            provider=result.provider,
            domain=result.domain,
            source_url=result.source_url,
            retrieved_at=result.retrieved_at,
            records=[],
            issues=[f"record_path not found: {spec.record_path}"],
            complete=False,
        )
    if not isinstance(raw_records, list):
        raise ValueError("normalization record_path must resolve to an array")
    records: list[dict[str, str | int | Decimal | bool | None]] = []
    issues: list[str] = []
    for index, raw_record in enumerate(raw_records):
        normalized: dict[str, str | int | Decimal | bool | None] = {}
        for mapping in spec.mappings:
            try:
                raw_value = _read_path(raw_record, mapping.source_path)
                normalized[mapping.target_field] = _normalize_value(
                    raw_value, mapping.data_type
                )
            except (KeyError, ValueError) as exc:
                if mapping.required:
                    issues.append(
                        f"record {index} field {mapping.target_field}: {exc}"
                    )
                else:
                    normalized[mapping.target_field] = None
        if not any(issue.startswith(f"record {index} ") for issue in issues):
            records.append(normalized)
    return NormalizedConnectorResult(
        connector_id=result.connector_id,
        request_id=result.request_id,
        provider=result.provider,
        domain=result.domain,
        source_url=result.source_url,
        retrieved_at=result.retrieved_at,
        records=records,
        issues=issues,
        complete=not issues,
    )
