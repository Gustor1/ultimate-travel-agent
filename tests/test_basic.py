"""Basic tests for package initialization."""

from ultimate_travel_agent import __version__


def test_version() -> None:
    """Check version is properly exposed."""
    assert __version__ == "1.0.0"
