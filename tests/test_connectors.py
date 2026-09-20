from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from urllib.request import Request

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.connectors import (
    ConnectorConfig,
    ConnectorFieldMapping,
    ConnectorNormalizationSpec,
    ConnectorRequest,
    ConnectorResult,
    execute_json_connector,
    normalize_connector_result,
)


class FakeResponse:
    def __init__(self, payload: Any, url: str, status: int = 200) -> None:
        self.payload = json.dumps(payload).encode()
        self.url = url
        self.status = status

    def read(self, amount: int = -1) -> bytes:
        return self.payload[:amount]

    def geturl(self) -> str:
        return self.url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _config(**updates: object) -> ConnectorConfig:
    data: dict[str, object] = {
        "connector_id": "flight-api",
        "provider": "Example Flights",
        "domain": "flights",
        "base_url": "https://api.example.com/v1/",
        "auth_mode": "bearer_env",
        "credential_env": "FLIGHT_API_TOKEN",
        "allowed_path_prefix": "/v1/",
    }
    data.update(updates)
    return ConnectorConfig.model_validate(data)


def test_live_connector_executes_json_without_exposing_bearer_secret() -> None:
    captured: dict[str, object] = {}

    def opener(request: Request, timeout: int) -> FakeResponse:
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return FakeResponse({"offers": [{"price": "499.00"}]}, request.full_url)

    result = execute_json_connector(
        _config(),
        ConnectorRequest(request_id="par-hkg", path="/v1/offers", query={"adults": 1}),
        environment={"FLIGHT_API_TOKEN": "super-secret"},
        open_url=opener,
    )
    assert result.payload == {"offers": [{"price": "499.00"}]}
    assert captured == {"authorization": "Bearer super-secret", "timeout": 20}
    assert "super-secret" not in result.model_dump_json()


def test_query_secret_is_removed_from_result_url() -> None:
    config = _config(
        auth_mode="query_env",
        auth_query_parameter="key",
    )

    def opener(request: Request, timeout: int) -> FakeResponse:
        assert "key=hidden" in request.full_url
        return FakeResponse([], request.full_url)

    result = execute_json_connector(
        config,
        ConnectorRequest(request_id="lookup", path="/v1/search"),
        environment={"FLIGHT_API_TOKEN": "hidden"},
        open_url=opener,
    )
    assert "hidden" not in str(result.source_url)
    assert "key=" not in str(result.source_url)


def test_connector_rejects_insecure_or_escaping_requests() -> None:
    with pytest.raises(ValidationError, match="HTTPS"):
        _config(base_url="http://api.example.com")
    with pytest.raises(ValidationError, match="traverse"):
        ConnectorRequest(request_id="bad", path="/v1/../admin")
    with pytest.raises(ValidationError, match="secrets"):
        ConnectorRequest(
            request_id="bad-header",
            path="/v1/search",
            headers={"Authorization": "secret"},
        )
    with pytest.raises(ValidationError, match="identity or payment"):
        ConnectorRequest(
            request_id="pii",
            path="/v1/search",
            json_body={"traveler": {"passport_number": "forbidden"}},
            method="POST",
        )


def test_connector_rejects_missing_secret_cross_host_redirect_and_large_body() -> None:
    request = ConnectorRequest(request_id="lookup", path="/v1/search")
    with pytest.raises(ValueError, match="missing connector credential"):
        execute_json_connector(_config(), request, environment={})

    def redirected(http_request: Request, timeout: int) -> FakeResponse:
        return FakeResponse({}, "https://evil.example/steal")

    with pytest.raises(ValueError, match="redirect changed host"):
        execute_json_connector(
            _config(),
            request,
            environment={"FLIGHT_API_TOKEN": "secret"},
            open_url=redirected,
        )

    config = _config(maximum_response_bytes=1024)

    def oversized(http_request: Request, timeout: int) -> FakeResponse:
        return FakeResponse({"data": "x" * 2000}, http_request.full_url)

    with pytest.raises(ValueError, match="exceeds"):
        execute_json_connector(
            config,
            request,
            environment={"FLIGHT_API_TOKEN": "secret"},
            open_url=oversized,
        )

    def server_error(http_request: Request, timeout: int) -> FakeResponse:
        return FakeResponse({"error": "unavailable"}, http_request.full_url, status=503)

    with pytest.raises(ValueError, match="HTTP status 503"):
        execute_json_connector(
            _config(),
            request,
            environment={"FLIGHT_API_TOKEN": "secret"},
            open_url=server_error,
        )


def test_connector_normalizes_provider_payload_with_exact_decimals() -> None:
    def opener(request: Request, timeout: int) -> FakeResponse:
        return FakeResponse(
            {"data": {"offers": [{"id": "offer-1", "price": "499.90", "stops": 1}]}},
            request.full_url,
        )

    result = execute_json_connector(
        _config(),
        ConnectorRequest(request_id="offers", path="/v1/offers"),
        environment={"FLIGHT_API_TOKEN": "secret"},
        open_url=opener,
    )
    normalized = normalize_connector_result(
        result,
        ConnectorNormalizationSpec(
            record_path="data.offers",
            mappings=[
                ConnectorFieldMapping(
                    target_field="offer_id", source_path="id", data_type="string"
                ),
                ConnectorFieldMapping(
                    target_field="total", source_path="price", data_type="decimal"
                ),
                ConnectorFieldMapping(
                    target_field="stops", source_path="stops", data_type="integer"
                ),
            ],
        ),
    )
    assert normalized.complete
    assert normalized.records[0]["total"] == Decimal("499.90")


def test_connector_normalization_drops_invalid_required_record() -> None:
    result = ConnectorResult.model_validate(
        {
            "connector_id": "hotel-api",
            "request_id": "hotels",
            "provider": "Hotels",
            "domain": "hotels",
            "source_url": "https://api.example.com/v1/hotels",
            "retrieved_at": "2026-09-20T10:00:00Z",
            "status_code": 200,
            "payload": [{"name": "Hotel without price"}],
        }
    )
    normalized = normalize_connector_result(
        result,
        ConnectorNormalizationSpec(
            mappings=[
                ConnectorFieldMapping(
                    target_field="price", source_path="price", data_type="decimal"
                )
            ]
        ),
    )
    assert not normalized.complete
    assert normalized.records == []
