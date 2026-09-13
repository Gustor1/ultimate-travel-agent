"""Tests for cloud deployment manifests, Docker configurations, and MCP client config examples."""

import json
import os
from pathlib import Path
import pytest
import yaml
from ultimate_travel_agent.integrations.models import ProviderConfigurationError
from ultimate_travel_agent.integrations.registry import default_registry


def test_mcp_config_examples_json_validity() -> None:
    """Validate that all example MCP config JSON files are valid and contain placeholders."""
    repo_root = Path(__file__).resolve().parent.parent
    configs_dir = repo_root / "examples" / "mcp-configs"
    assert configs_dir.exists()

    expected_files = [
        "antigravity.local.json",
        "antigravity.remote.json",
        "claude-code.local.json",
        "claude-code.remote.json",
        "cursor.remote.json",
    ]

    for filename in expected_files:
        path = configs_dir / filename
        assert path.exists(), f"Missing config example: {filename}"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "mcpServers" in data

        if "remote" in filename:
            content = path.read_text(encoding="utf-8")
            assert "https://YOUR-TRAVEL-MCP-DOMAIN/mcp" in content
            assert "YOUR_TRAVEL_MCP_API_KEY" in content or "Bearer" in content
            # Ensure no real domain or token was leaked
            assert "sk-" not in content
            assert "localhost" not in content


def test_dockerfile_contents() -> None:
    """Validate Dockerfile instructions and non-root security posture."""
    repo_root = Path(__file__).resolve().parent.parent
    dockerfile = repo_root / "Dockerfile"
    assert dockerfile.exists()

    content = dockerfile.read_text(encoding="utf-8")
    assert "FROM python:" in content
    assert "useradd" in content
    assert "USER traveler" in content
    assert "HEALTHCHECK" in content
    assert "EXPOSE" in content
    assert "mcp-http" in content
    # Ensure no secrets were copied into image
    assert "COPY .env" not in content
    assert "ADD .env" not in content


def test_docker_compose_validity() -> None:
    """Validate docker-compose.yml YAML syntax and properties."""
    repo_root = Path(__file__).resolve().parent.parent
    compose_file = repo_root / "docker-compose.yml"
    assert compose_file.exists()

    with open(compose_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "services" in data
    assert "ultimate-travel-mcp" in data["services"]
    svc = data["services"]["ultimate-travel-mcp"]
    assert "healthcheck" in svc
    assert "ports" in svc


def test_cloud_deployment_manifests() -> None:
    """Validate deployment manifests for Railway, Render, Cloud Run, and Fly.io."""
    repo_root = Path(__file__).resolve().parent.parent
    deploy_dir = repo_root / "deployment"
    assert deploy_dir.exists()

    # 1. Railway
    railway_file = deploy_dir / "railway.json"
    assert railway_file.exists()
    with open(railway_file, "r", encoding="utf-8") as f:
        railway_data = json.load(f)
    assert railway_data["deploy"]["healthcheckPath"] == "/health"

    # 2. Render
    render_file = deploy_dir / "render.yaml"
    assert render_file.exists()
    with open(render_file, "r", encoding="utf-8") as f:
        render_data = yaml.safe_load(f)
    assert render_data["services"][0]["healthCheckPath"] == "/health"

    # 3. Cloud Run
    cloudrun_file = deploy_dir / "cloudrun.yaml"
    assert cloudrun_file.exists()
    with open(cloudrun_file, "r", encoding="utf-8") as f:
        cloudrun_data = yaml.safe_load(f)
    assert cloudrun_data["kind"] == "Service"

    # 4. Fly.io
    fly_file = deploy_dir / "fly.toml"
    assert fly_file.exists()
    fly_text = fly_file.read_text(encoding="utf-8")
    assert 'path = "/health"' in fly_text


def test_providers_example_yaml() -> None:
    """Validate config/providers.example.yaml structure."""
    repo_root = Path(__file__).resolve().parent.parent
    providers_yaml = repo_root / "config" / "providers.example.yaml"
    assert providers_yaml.exists()

    with open(providers_yaml, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["default_mode"] == "offline"
    providers = data["providers"]
    for cat in ["flights", "trains", "accommodations", "reviews", "activities", "maps", "weather", "currency"]:
        assert cat in providers
        assert "active_provider" in providers[cat]
        assert providers[cat]["fallback_to_mock"] is True


def test_provider_registry_env_selection() -> None:
    """Test runtime provider selection via TRAVEL_PROVIDER_* environment variables."""
    # Test weather override
    os.environ["TRAVEL_PROVIDER_WEATHER"] = "open_meteo"
    weather_prov = default_registry.get_default_provider("weather")
    assert weather_prov is not None
    assert weather_prov.name == "open_meteo"
    os.environ.pop("TRAVEL_PROVIDER_WEATHER")

    # Test maps override with alias
    os.environ["TRAVEL_PROVIDER_MAPS"] = "ors"
    maps_prov = default_registry.get_default_provider("map")
    assert maps_prov is not None
    assert maps_prov.name == "openrouteservice"
    os.environ.pop("TRAVEL_PROVIDER_MAPS")

    # Test flights override
    os.environ["TRAVEL_PROVIDER_FLIGHTS"] = "amadeus"
    flights_prov = default_registry.get_default_provider("flight")
    assert flights_prov is not None
    assert flights_prov.name == "amadeus_flight"
    os.environ.pop("TRAVEL_PROVIDER_FLIGHTS")

    # Test that missing key in live mode raises ProviderConfigurationError
    with pytest.raises(ProviderConfigurationError):
        flights_prov.execute_query(
            mode="live",
            origin="PAR",
            destination="BCN",
            departure_date="2026-10-15",
        )
