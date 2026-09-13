"""Tests for Phase 10 keyless live public data providers (Open-Meteo, ECB, Wikivoyage, Nominatim, OSRM).

STRICT SAFETY: All tests run 100% offline using unit test mocks. Zero live network calls.
"""

from io import BytesIO
import json
import os
import urllib.error
from unittest.mock import MagicMock, patch
import pytest

from ultimate_travel_agent.integrations import (
    CacheStatus,
    ECBCurrencyProvider,
    NominatimProvider,
    OpenMeteoProvider,
    OSRMProvider,
    ProviderConfigurationError,
    ProviderMode,
    ProviderNetworkError,
    ProviderRateLimitError,
    ResultStatus,
    WikivoyageProvider,
    default_registry,
)
from ultimate_travel_agent.integrations.http_client import KeylessHttpClient


# ---------------------------------------------------------------------------
# Open-Meteo Tests
# ---------------------------------------------------------------------------

def test_open_meteo_live_forecast_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Open-Meteo live weather forecast and geocoding integration with mock HTTP."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_OPEN_METEO", "true")

    client = KeylessHttpClient(user_agent="TestAgent/1.0", default_timeout=2.0)
    client.clear_cache()
    provider = OpenMeteoProvider(mode=ProviderMode.LIVE, http_client=client)
    assert provider.is_configured() is True

    geo_data = {
        "results": [
            {
                "name": "Barcelona",
                "latitude": 41.3887,
                "longitude": 2.1590,
                "country": "Spain",
                "timezone": "Europe/Madrid",
                "admin1": "Catalonia",
            }
        ]
    }
    forecast_data = {
        "current": {
            "temperature_2m": 22.4,
            "relative_humidity_2m": 60,
            "precipitation": 0.0,
            "weather_code": 1,
            "wind_speed_10m": 11.2,
        },
        "daily": {
            "time": ["2026-10-15", "2026-10-16"],
            "weather_code": [1, 61],
            "temperature_2m_max": [24.0, 20.0],
            "temperature_2m_min": [16.0, 14.5],
            "precipitation_sum": [0.0, 4.2],
            "precipitation_probability_max": [10, 75],
            "wind_speed_10m_max": [14.0, 18.5],
        },
    }

    def mock_get(url: str, **kwargs):
        if "geocoding-api" in url:
            return geo_data, "miss"
        return forecast_data, "miss"

    monkeypatch.setattr(client, "get", mock_get)

    result = provider.search(city="Barcelona", days=2)
    assert result.provider == "open_meteo"
    assert result.mode == "live"
    assert result.attribution == "Weather data by Open-Meteo.com under CC BY 4.0 (https://open-meteo.com/)"
    assert result.source_url == "https://open-meteo.com/"
    assert result.result_status == ResultStatus.LIVE.value
    assert len(result.items) == 3  # 1 current + 2 daily

    curr = result.items[0]
    assert curr.details["temperature"] == 22.4
    assert curr.details["condition"] == "Mainly clear"

    rain_day = result.items[2]
    assert rain_day.details["rain_risk"] is True
    assert rain_day.details["indoor_plan_b_recommended"] is True
    assert "Plan B" in rain_day.description


def test_open_meteo_geocoding_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test graceful handling when a city is not found in geocoding."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_OPEN_METEO", "true")

    client = KeylessHttpClient()
    provider = OpenMeteoProvider(mode=ProviderMode.LIVE, http_client=client)

    monkeypatch.setattr(client, "get", lambda url, **kwargs: ({"results": []}, "miss"))

    result = provider.search(city="UnknownCity12345")
    assert result.total_results == 0
    assert result.result_status == ResultStatus.UNAVAILABLE.value
    assert any("could not be resolved" in w for w in result.warnings)


def test_open_meteo_disabled_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that live mode fails closed if keyless toggle is disabled."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "false")
    provider = OpenMeteoProvider(mode=ProviderMode.LIVE)
    assert provider.is_configured() is False

    with pytest.raises(ProviderConfigurationError) as exc_info:
        provider.search(city="Paris")
    assert "disabled or unconfigured" in str(exc_info.value)


def test_open_meteo_offline_mode() -> None:
    """Test that offline mode returns deterministic simulation with license metadata."""
    provider = OpenMeteoProvider(mode=ProviderMode.OFFLINE)
    res = provider.search(city="Paris")
    assert res.provider == "open_meteo"
    assert res.attribution is not None
    assert len(res.items) >= 1


# ---------------------------------------------------------------------------
# ECB Currency Tests
# ---------------------------------------------------------------------------

SAMPLE_ECB_XML = """<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
  <Cube>
    <Cube time="2026-09-11">
      <Cube currency="USD" rate="1.0850"/>
      <Cube currency="JPY" rate="162.50"/>
      <Cube currency="GBP" rate="0.8400"/>
      <Cube currency="CHF" rate="0.9500"/>
    </Cube>
  </Cube>
</gesmes:Envelope>
"""


def test_ecb_live_conversion_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ECB exchange rate parsing, cross-rates calculation, and card fee disclaimers."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_ECB", "true")

    client = KeylessHttpClient()
    client.clear_cache()
    provider = ECBCurrencyProvider(mode=ProviderMode.LIVE, http_client=client)
    assert provider.is_configured() is True

    monkeypatch.setattr(client, "get", lambda url, **kwargs: (SAMPLE_ECB_XML, "miss"))

    # Convert EUR to USD
    res = provider.search(amount=100.0, from_currency="EUR", to_currency="USD")
    assert res.provider == "ecb_currency"
    assert res.mode == "live"
    assert len(res.items) == 1
    item = res.items[0]
    assert item.price == 108.50
    assert item.details["rate_date"] == "2026-09-11"
    assert "1.5% - 3.5%" in item.details["advisory"]
    assert res.attribution is not None

    # Convert cross-currency USD to GBP (1.085 USD/EUR, 0.84 GBP/EUR -> rate = 0.84 / 1.085)
    res_cross = provider.search(amount=108.50, from_currency="USD", to_currency="GBP")
    assert round(res_cross.items[0].price, 2) == 84.00


def test_ecb_missing_currency_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test fallback when target currency is not present in ECB feed."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_ECB", "true")

    client = KeylessHttpClient()
    provider = ECBCurrencyProvider(mode=ProviderMode.LIVE, http_client=client)

    # XML without ISK
    monkeypatch.setattr(client, "get", lambda url, **kwargs: (SAMPLE_ECB_XML, "miss"))

    res = provider.search(amount=100.0, from_currency="EUR", to_currency="ISK")
    assert res.total_results == 1
    assert any("missing from ECB feed" in w for w in res.warnings)


def test_ecb_disabled_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that live ECB conversion fails closed if toggled off."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "false")
    provider = ECBCurrencyProvider(mode=ProviderMode.LIVE)
    assert provider.is_configured() is False

    with pytest.raises(ProviderConfigurationError):
        provider.search(amount=50.0, from_currency="EUR", to_currency="USD")


# ---------------------------------------------------------------------------
# Wikivoyage Tests
# ---------------------------------------------------------------------------

def test_wikivoyage_live_search_and_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Wikivoyage search and summary with CC BY-SA 4.0 attribution and community disclaimer."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_WIKIVOYAGE", "true")

    client = KeylessHttpClient()
    client.clear_cache()
    provider = WikivoyageProvider(mode=ProviderMode.LIVE, http_client=client)
    assert provider.is_configured() is True

    summary_payload = {
        "query": {
            "pages": {
                "1234": {
                    "pageid": 1234,
                    "title": "Barcelona",
                    "extract": "Barcelona is the capital and largest city of Catalonia in northeastern Spain.",
                }
            }
        }
    }

    monkeypatch.setattr(client, "get", lambda url, **kwargs: (summary_payload, "miss"))

    res = provider.search(city="Barcelona")
    assert res.provider == "wikivoyage"
    assert res.mode == "live"
    assert len(res.items) == 1
    item = res.items[0]
    assert "Barcelona" in item.title
    assert "Catalonia" in item.description
    assert item.verification_level == "community_recommended"
    assert "CC BY-SA 4.0" in item.attribution
    assert any("Community-curated" in w for w in res.warnings)


def test_wikivoyage_disabled_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that live Wikivoyage query fails closed when disabled."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "false")
    provider = WikivoyageProvider(mode=ProviderMode.LIVE)
    with pytest.raises(ProviderConfigurationError):
        provider.search(city="Barcelona")


# ---------------------------------------------------------------------------
# Nominatim (Limited) Tests
# ---------------------------------------------------------------------------

def test_nominatim_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Nominatim is strictly limited and disabled by default."""
    monkeypatch.delenv("TRAVEL_MCP_ENABLE_NOMINATIM", raising=False)
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")

    provider = NominatimProvider(mode=ProviderMode.LIVE)
    assert provider.is_configured() is False

    with pytest.raises(ProviderConfigurationError) as exc_info:
        provider.search(query="Sagrada Familia")
    assert "DISABLED by default" in str(exc_info.value)


def test_nominatim_live_when_explicitly_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Nominatim geocoding when explicitly enabled with 1 req/s rule and ODbL attribution."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_NOMINATIM", "true")

    client = KeylessHttpClient()
    provider = NominatimProvider(mode=ProviderMode.LIVE, http_client=client)
    assert provider.is_configured() is True

    mock_osm_data = [
        {
            "display_name": "Basilica de la Sagrada Familia, Barcelona, Spain",
            "lat": "41.4036",
            "lon": "2.1744",
            "osm_type": "way",
            "osm_id": 123456,
        }
    ]
    monkeypatch.setattr(client, "get", lambda url, **kwargs: (mock_osm_data, "miss"))

    res = provider.search(query="Sagrada Familia")
    assert res.provider == "nominatim"
    assert res.mode == "live"
    assert len(res.items) == 1
    assert "OpenStreetMap contributors" in res.attribution
    assert "ODbL" in res.attribution
    assert res.items[0].details["latitude"] == 41.4036


# ---------------------------------------------------------------------------
# OSRM (Experimental) Tests
# ---------------------------------------------------------------------------

def test_osrm_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that OSRM demo routing is disabled by default."""
    monkeypatch.delenv("TRAVEL_MCP_ENABLE_OSRM", raising=False)
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")

    provider = OSRMProvider(mode=ProviderMode.LIVE)
    assert provider.is_configured() is False

    with pytest.raises(ProviderConfigurationError) as exc_info:
        provider.search(origin="Paris", destination="Lyon")
    assert "DISABLED by default" in str(exc_info.value)


def test_osrm_live_routing_and_fatigue_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test OSRM routing when explicitly enabled, including fatigue warning for routes > 4h."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_OSRM", "true")

    client = KeylessHttpClient()
    provider = OSRMProvider(mode=ProviderMode.LIVE, http_client=client)
    assert provider.is_configured() is True

    # 465 km, 16200 seconds (4.5 hours)
    mock_osrm_res = {
        "code": "Ok",
        "routes": [
            {
                "distance": 465000.0,
                "duration": 16200.0,
            }
        ],
    }
    monkeypatch.setattr(client, "get", lambda url, **kwargs: (mock_osrm_res, "miss"))

    res = provider.search(origin="Paris", destination="Lyon")
    assert res.provider == "osrm"
    assert res.mode == "live"
    assert res.items[0].details["distance_km"] == 465.0
    assert res.items[0].details["duration_hours"] == 4.5
    assert res.items[0].details["fatigue_warning"] is True
    assert any("exceeds 4 hours" in w for w in res.warnings)
    assert any("NO SLA" in w for w in res.warnings)


# ---------------------------------------------------------------------------
# HTTP Client: Security, Caching, Rate Limiting & Error Handling Tests
# ---------------------------------------------------------------------------

def test_http_client_https_enforcement() -> None:
    """Test that unencrypted plain HTTP requests to external endpoints are rejected."""
    client = KeylessHttpClient()
    with pytest.raises(ValueError) as exc_info:
        client.get("http://api.insecure-provider.org/data")
    assert "Insecure scheme" in str(exc_info.value)


def test_http_client_cache_hit_and_stale_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that repeat queries hit cache, and network errors fall back to stale cache."""
    client = KeylessHttpClient()
    client.clear_cache()

    url = "https://api.open-meteo.com/v1/forecast?city=test"

    # 1. Initial miss
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"status": "ok"}'
    mock_resp.headers.get_content_charset.return_value = "utf-8"
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        data1, status1 = client.get(url, ttl_seconds=10)
        assert data1 == {"status": "ok"}
        assert status1 == CacheStatus.MISS.value

    # 2. Subsequent hit without network call
    data2, status2 = client.get(url, ttl_seconds=10)
    assert data2 == {"status": "ok"}
    assert status2 == CacheStatus.HIT.value

    # 3. Simulate network error with expired cache -> falls back to stale
    with client._cache_lock:
        client._cache[url]["expires_at"] = 0  # Force expiration

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("DNS failure")):
        data3, status3 = client.get(url)
        assert data3 == {"status": "ok"}
        assert status3 == CacheStatus.STALE.value


def test_http_client_429_rate_limit_handling() -> None:
    """Test that HTTP 429 raises ProviderRateLimitError."""
    client = KeylessHttpClient()
    client.clear_cache()
    url = "https://api.open-meteo.com/v1/forecast?rate_limited=true"

    err = urllib.error.HTTPError(url, 429, "Too Many Requests", {}, BytesIO(b""))
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(ProviderRateLimitError) as exc_info:
            client.get(url)
        assert "429" in str(exc_info.value)


def test_http_client_5xx_server_error_handling() -> None:
    """Test that HTTP 500 without cache raises ProviderNetworkError."""
    client = KeylessHttpClient()
    client.clear_cache()
    url = "https://api.open-meteo.com/v1/forecast?server_err=true"

    err = urllib.error.HTTPError(url, 502, "Bad Gateway", {}, BytesIO(b""))
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(ProviderNetworkError) as exc_info:
            client.get(url)
        assert "502" in str(exc_info.value)


def test_cache_response_retrieved_at_and_unpacking() -> None:
    """Test CacheResponse preserves retrieved_at while remaining 2-tuple unpackable."""
    from ultimate_travel_agent.integrations.http_client import CacheResponse

    resp = CacheResponse({"temp": 20}, "hit", "2026-09-13T20:00:00Z")
    # Unpack as 2-tuple (data, cache_status)
    data, cache_status = resp
    assert data == {"temp": 20}
    assert cache_status == "hit"
    assert resp.retrieved_at == "2026-09-13T20:00:00Z"


def test_rate_tuple_and_search_result_list_metadata() -> None:
    """Test RateTuple and SearchResultList preserve retrieved_at and cache_status."""
    from ultimate_travel_agent.integrations.currency.ecb import RateTuple
    from ultimate_travel_agent.integrations.guides.wikivoyage import SearchResultList

    rt = RateTuple({"USD": 1.1}, "2026-09-13", "hit", "2026-09-13T12:00:00Z")
    rates, rate_date, cache_status = rt
    assert rates == {"USD": 1.1}
    assert rate_date == "2026-09-13"
    assert cache_status == "hit"
    assert rt.retrieved_at == "2026-09-13T12:00:00Z"

    srl = SearchResultList([{"title": "Tokyo"}], cache_status="miss", retrieved_at="2026-09-13T12:00:00Z")
    assert len(srl) == 1
    assert srl[0]["title"] == "Tokyo"
    assert srl.cache_status == "miss"
    assert srl.retrieved_at == "2026-09-13T12:00:00Z"


def test_osrm_unresolvable_coordinates_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test OSRMProvider handles unknown city coordinates gracefully by returning UNAVAILABLE."""
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "true")
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_OSRM", "true")

    provider = OSRMProvider(mode=ProviderMode.LIVE)
    res = provider.search(origin="NonExistentCityA", destination="NonExistentCityB")
    assert res.result_status == ResultStatus.UNAVAILABLE.value
    assert len(res.items) == 0
    assert any("Could not resolve coordinates" in w for w in res.warnings)

