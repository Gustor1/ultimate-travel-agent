"""Secure, rate-limited, and cached HTTP client utility for keyless public providers."""

from datetime import datetime, timezone
import json
import os
import ssl
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.error
import urllib.parse
import urllib.request

from ultimate_travel_agent.integrations.models import (
    CacheStatus,
    ProviderNetworkError,
    ProviderRateLimitError,
)

DEFAULT_USER_AGENT = "UltimateTravelAgent/1.0 (https://github.com/Gustor1/ultimate-travel-agent)"
DEFAULT_TIMEOUT_SECONDS = 5.0


class RateLimiter:
    """Thread-safe rate limiter enforcing a minimum time interval between requests."""

    def __init__(self, min_interval_seconds: float = 0.0) -> None:
        self.min_interval = min_interval_seconds
        self.last_call = 0.0
        self.lock = threading.Lock()

    def acquire(self) -> None:
        """Wait until minimum interval has passed since the last call."""
        if self.min_interval <= 0:
            return
        with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()


class KeylessHttpClient:
    """Standard client for public keyless APIs with caching, rate limiting, and timeout safety."""

    _instance: Optional["KeylessHttpClient"] = None
    _singleton_lock = threading.Lock()

    def __init__(
        self,
        user_agent: Optional[str] = None,
        default_timeout: Optional[float] = None,
    ) -> None:
        self.user_agent = user_agent or os.getenv("TRAVEL_MCP_HTTP_USER_AGENT") or DEFAULT_USER_AGENT
        self.default_timeout = default_timeout or float(
            os.getenv("TRAVEL_HTTP_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS))
        )
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        self._limiters: Dict[str, RateLimiter] = {
            "nominatim": RateLimiter(min_interval_seconds=1.0),   # OSM Nominatim policy: 1 req/sec max
            "open_meteo": RateLimiter(min_interval_seconds=0.2),  # 5 req/sec burst
            "ecb": RateLimiter(min_interval_seconds=0.5),         # 2 req/sec
            "wikivoyage": RateLimiter(min_interval_seconds=0.33), # 3 req/sec
            "osrm": RateLimiter(min_interval_seconds=1.0),        # 1 req/sec demo server
        }

    @classmethod
    def get_instance(cls) -> "KeylessHttpClient":
        """Singleton accessor for shared caching and rate limiting."""
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def clear_cache(self) -> None:
        """Clear all in-memory cache entries."""
        with self._cache_lock:
            self._cache.clear()

    def _get_limiter(self, domain_or_service: str, min_interval: float = 0.0) -> RateLimiter:
        key = domain_or_service.lower()
        if key not in self._limiters:
            self._limiters[key] = RateLimiter(min_interval_seconds=min_interval)
        return self._limiters[key]

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        ttl_seconds: int = 1800,
        service_name: Optional[str] = None,
        min_interval_seconds: float = 0.0,
        parse_json: bool = True,
    ) -> Tuple[Union[Dict[str, Any], List[Any], str], str]:
        """Perform a safe GET request with caching, HTTPS verification, and rate limiting.

        Returns:
            Tuple of (response_content, cache_status) where cache_status is 'hit', 'miss', or 'stale'.
        """
        parsed = urllib.parse.urlparse(url)
        # Enforce HTTPS (allow localhost / 127.0.0.1 for mock/testing)
        if parsed.scheme.lower() != "https":
            if parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
                raise ValueError(
                    f"Insecure scheme '{parsed.scheme}' rejected. Public keyless providers must use HTTPS."
                )

        # Build query string
        full_url = url
        if params:
            clean_params = {k: v for k, v in sorted(params.items()) if v is not None}
            query_str = urllib.parse.urlencode(clean_params)
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}{query_str}"

        cache_key = full_url

        # Check Cache
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached:
                now = time.time()
                if now < cached["expires_at"]:
                    return cached["data"], CacheStatus.HIT.value

        # Apply rate limiting
        svc = service_name or parsed.netloc
        limiter = self._get_limiter(svc, min_interval=min_interval_seconds)
        limiter.acquire()

        # Prepare request
        req_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, application/xml, text/xml, */*",
        }
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(full_url, headers=req_headers, method="GET")
        req_timeout = timeout or self.default_timeout

        try:
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=req_timeout, context=ctx) as resp:
                raw_bytes = resp.read()
                encoding = resp.headers.get_content_charset() or "utf-8"
                text = raw_bytes.decode(encoding, errors="replace")

                data: Union[Dict[str, Any], List[Any], str]
                if parse_json:
                    try:
                        data = json.loads(text)
                    except Exception as json_err:
                        raise ProviderNetworkError(
                            f"Invalid JSON response from {parsed.netloc}: {str(json_err)}"
                        ) from json_err
                else:
                    data = text

                # Update cache
                with self._cache_lock:
                    self._cache[cache_key] = {
                        "data": data,
                        "expires_at": time.time() + ttl_seconds,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    }

                return data, CacheStatus.MISS.value

        except urllib.error.HTTPError as http_err:
            if http_err.code == 429:
                # Rate limited
                with self._cache_lock:
                    if cached:
                        return cached["data"], CacheStatus.STALE.value
                raise ProviderRateLimitError(
                    f"External rate limit encountered (HTTP 429) for provider '{svc}' at {url}."
                ) from http_err
            elif http_err.code >= 500:
                with self._cache_lock:
                    if cached:
                        return cached["data"], CacheStatus.STALE.value
                raise ProviderNetworkError(
                    f"External server error (HTTP {http_err.code}) from provider '{svc}'."
                ) from http_err
            else:
                with self._cache_lock:
                    if cached:
                        return cached["data"], CacheStatus.STALE.value
                raise ProviderNetworkError(
                    f"HTTP error {http_err.code} ({http_err.reason}) from provider '{svc}'."
                ) from http_err

        except (urllib.error.URLError, TimeoutError, OSError) as net_err:
            # Fallback to stale cache if available
            with self._cache_lock:
                if cached:
                    return cached["data"], CacheStatus.STALE.value
            raise ProviderNetworkError(
                f"Network communication failure for '{svc}' at {url}: {str(net_err)}"
            ) from net_err
