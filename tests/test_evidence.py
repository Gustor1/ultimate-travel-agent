import pytest

from ultimate_travel_agent.evidence import canonicalize_source_url


def test_canonicalize_source_url_removes_tracking_but_preserves_semantics() -> None:
    canonical = canonicalize_source_url(
        "HTTPS://Example.COM:443/booking?utm_source=search&date=2026-10-03&gclid=x&room=double#offers"
    )
    assert canonical == "https://example.com/booking?date=2026-10-03&room=double"


def test_canonicalize_source_url_sorts_query_and_deduplicates_pairs() -> None:
    canonical = canonicalize_source_url(
        "https://example.com/path?room=double&date=2026-10-03&room=double"
    )
    assert canonical == "https://example.com/path?date=2026-10-03&room=double"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/file",
        "https://user:secret@example.com/path",
        "https:///missing-host",
    ],
)
def test_canonicalize_source_url_rejects_unsafe_or_invalid_urls(url: str) -> None:
    with pytest.raises(ValueError):
        canonicalize_source_url(url)
