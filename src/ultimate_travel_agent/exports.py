"""Portable, deterministic exports for calendars, maps, checklists, and offline use."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from typing import Any

from ultimate_travel_agent.contracts import TravelDossierV1


def _ics_escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_datetime(value: object) -> str:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("calendar event times must include a timezone offset")
    return parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_ics(dossier: TravelDossierV1) -> str:
    """Export itinerary rows to an RFC 5545-compatible UTC calendar."""

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ultimate Travel Agent//EN"]
    for index, item in enumerate(dossier.itinerary, start=1):
        if not all(key in item for key in ("title", "start", "end")):
            continue
        identity = str(item.get("item_id", f"item-{index}"))
        uid = sha256(f"{identity}|{item['start']}".encode()).hexdigest()[:24]
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}@ultimate-travel-agent",
                f"DTSTART:{_ics_datetime(item['start'])}",
                f"DTEND:{_ics_datetime(item['end'])}",
                f"SUMMARY:{_ics_escape(item['title'])}",
            ]
        )
        if item.get("location"):
            lines.append(f"LOCATION:{_ics_escape(item['location'])}")
        if item.get("description"):
            lines.append(f"DESCRIPTION:{_ics_escape(item['description'])}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def export_geojson(dossier: TravelDossierV1) -> dict[str, Any]:
    """Export dossier locations as a GeoJSON FeatureCollection."""

    features: list[dict[str, Any]] = []
    for location in dossier.locations:
        if "latitude" not in location or "longitude" not in location:
            continue
        properties = {
            key: value for key, value in location.items() if key not in {"latitude", "longitude"}
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [location["longitude"], location["latitude"]],
                },
                "properties": properties,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def export_checklist(dossier: TravelDossierV1) -> str:
    """Build a booking checklist from unresolved dossier state."""

    rows = ["# Booking checklist", ""]
    items = [
        *(f"Verify: {item}" for item in dossier.verification_required),
        *(f"Resolve: {item}" for item in dossier.readiness.blockers),
        *(f"Obtain: {item}" for item in dossier.missing_information),
    ]
    rows.extend(f"- [ ] {item}" for item in items)
    if not items:
        rows.append("- [x] No unresolved booking checks")
    return "\n".join(rows) + "\n"


def export_offline_bundle(dossier: TravelDossierV1) -> dict[str, Any]:
    """Create a self-contained JSON-safe pack with direct source links."""

    return {
        "format": "ultimate-travel-agent/offline-v1",
        "dossier": dossier.model_dump(mode="json"),
        "direct_links": [str(source.url) for source in dossier.sources],
        "checklist": export_checklist(dossier),
    }


def export_mobile_html(dossier: TravelDossierV1) -> str:
    """Create a self-contained responsive summary with safe direct links."""

    itinerary = "".join(
        f"<li><strong>{escape(str(item.get('title', 'Plan item')))}</strong>"
        f"<br><small>{escape(str(item.get('start', '')))} — "
        f"{escape(str(item.get('end', '')))}</small></li>"
        for item in dossier.itinerary
    ) or "<li>No itinerary items</li>"
    links = "".join(
        f'<li><a href="{escape(str(source.url), quote=True)}">'
        f"{escape(source.name)}</a></li>"
        for source in dossier.sources
    ) or "<li>No source links</li>"
    checks = "".join(
        f"<li>☐ {escape(item)}</li>"
        for item in [*dossier.verification_required, *dossier.readiness.blockers]
    ) or "<li>☑ No unresolved checks</li>"
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Travel plan</title><style>body{{font:16px system-ui;max-width:48rem;margin:auto;padding:1rem;line-height:1.5}}li{{margin:.6rem 0}}a{{overflow-wrap:anywhere}}@media(prefers-color-scheme:dark){{body{{background:#111;color:#eee}}a{{color:#8cc8ff}}}}</style>
<main><h1>Travel plan</h1><p>{escape(dossier.summary)}</p><h2>Itinerary</h2><ol>{itinerary}</ol><h2>Checks</h2><ul>{checks}</ul><h2>Direct sources</h2><ul>{links}</ul></main></html>"""


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def export_pdf(dossier: TravelDossierV1) -> bytes:
    """Produce a dependency-free, text-only PDF summary."""

    raw_lines = [dossier.summary, "", *dossier.recommendations, "", *dossier.risks]
    lines = [re.sub(r"\s+", " ", str(line)).strip()[:100] for line in raw_lines if str(line).strip()]
    commands = ["BT", "/F1 11 Tf", "50 790 Td"]
    for index, line in enumerate(lines[:42]):
        if index:
            commands.append("0 -17 Td")
        commands.append(f"({_pdf_escape(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(output)


def serialize_export(dossier: TravelDossierV1, export_format: str) -> bytes:
    """Dispatch one supported export format to bytes."""

    if export_format == "ics":
        return export_ics(dossier).encode()
    if export_format == "geojson":
        return json.dumps(export_geojson(dossier), ensure_ascii=False, indent=2).encode()
    if export_format == "checklist":
        return export_checklist(dossier).encode()
    if export_format == "offline":
        return json.dumps(export_offline_bundle(dossier), ensure_ascii=False, indent=2).encode()
    if export_format == "html":
        return export_mobile_html(dossier).encode()
    if export_format == "pdf":
        return export_pdf(dossier)
    raise ValueError(f"unsupported export format: {export_format}")
