"""Basic sanity tests for package metadata and CLI entry points."""

import os
import subprocess
import sys
from pathlib import Path

from ultimate_travel_agent import __version__
from ultimate_travel_agent.cli import get_base_dir

REPO_ROOT = Path(__file__).resolve().parent.parent


def _source_environment() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    source = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = source if not existing else f"{source}{os.pathsep}{existing}"
    return env


def test_package_metadata():
    """Verify package version and base directory resolution."""
    assert __version__ is not None
    base_dir = get_base_dir()
    assert (base_dir / ".agents").exists()


def test_cli_help():
    """Verify CLI --help runs cleanly with zero exit code."""
    result = subprocess.run(
        [sys.executable, "-m", "ultimate_travel_agent.cli", "--help"],
        capture_output=True,
        text=True,
        env=_source_environment(),
    )
    assert result.returncode == 0
    assert "install-skills" in result.stdout
    assert "uninstall-skills" in result.stdout
    assert "list-skills" in result.stdout
    assert "flight-search-plan" in result.stdout
    assert "flight-search-coverage" in result.stdout
    assert "hotel-search-plan" in result.stdout
    assert "hotel-search-coverage" in result.stdout
    assert "hotel-compare" in result.stdout
    assert "connector-fetch" in result.stdout
    assert "adaptive-day" in result.stdout
    assert "group-decide" in result.stdout
    assert "neighborhood-score" in result.stdout
    assert "booking-handoff" in result.stdout
    assert "trip-mode" in result.stdout
    assert "route-optimize" in result.stdout
    assert "notify-webhook" in result.stdout


def test_cli_list_skills():
    """Verify list-skills subcommand outputs all 14 skills."""
    result = subprocess.run(
        [sys.executable, "-m", "ultimate_travel_agent.cli", "list-skills"],
        capture_output=True,
        text=True,
        env=_source_environment(),
    )
    assert result.returncode == 0
    assert "travel-orchestrator" in result.stdout
    assert "travel-web-research" in result.stdout
    assert "transport-research" in result.stdout
    assert "accommodation-research" in result.stdout
    assert "activity-curator" in result.stdout
    assert "itinerary-builder" in result.stdout
    assert "budget-and-booking-checker" in result.stdout
    assert "travel-safety" in result.stdout
    assert "source-verification" in result.stdout
    assert "travel-quality-control" in result.stdout
    assert "flight-search" in result.stdout
