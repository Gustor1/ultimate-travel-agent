"""Deterministic evidence normalization helpers."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "msclkid"}


def canonicalize_source_url(url: str) -> str:
    """Remove non-semantic URL noise while preserving source identity.

    The original URL remains the evidence locator; this canonical form is only
    a deduplication key.  Product, date, language, fare, and other unknown query
    parameters are deliberately preserved.
    """

    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("source URL must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("source URL must not contain credentials")

    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("source URL contains an invalid port") from exc
    if port is not None and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        host = f"{host}:{port}"

    semantic_pairs = {
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_KEYS and not key.lower().startswith("utm_")
    }
    query = urlencode(sorted(semantic_pairs))
    return urlunsplit((scheme, host, parsed.path, query, ""))
