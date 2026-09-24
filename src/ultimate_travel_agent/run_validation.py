"""Validate durable travel-run manifests and their declared artifacts."""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

GATE_ORDER = (
    "coverage_complete",
    "evidence_sufficient",
    "recommendation_ready",
    "booking_ready",
)
RECOMMENDATION_ARTIFACTS = ("sources", "research", "decisions", "checks")


def _artifact_paths(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [path for item in value for path in _artifact_paths(item)]
    if isinstance(value, dict):
        return [path for item in value.values() for path in _artifact_paths(item)]
    return []


def validate_run(run_dir: Path) -> tuple[bool, list[str]]:
    """Check a travel-run/v1 manifest, gate order, and declared local files."""

    issues: list[str] = []
    root = run_dir.resolve()
    manifest_path = root / "manifest.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return False, [f"Cannot read manifest.yaml: {exc}"]
    if not isinstance(manifest, dict):
        return False, ["manifest.yaml must contain a mapping"]
    if manifest.get("schema") != "travel-run/v1":
        issues.append("schema must be travel-run/v1")
    if manifest.get("run_id") != root.name:
        issues.append("run_id must match the run directory name")

    gates = manifest.get("gates")
    if not isinstance(gates, dict):
        issues.append("gates must be a mapping")
        gates = {}
    for gate in GATE_ORDER:
        if type(gates.get(gate)) is not bool:
            issues.append(f"gates.{gate} must be a boolean")
    for prerequisite, dependent in pairwise(GATE_ORDER):
        if gates.get(dependent) is True and gates.get(prerequisite) is not True:
            issues.append(f"{dependent} requires {prerequisite}")
    if gates.get("booking_ready") is True and manifest.get("blockers"):
        issues.append("booking_ready requires no blockers")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append("artifacts must be a mapping")
        artifacts = {}
    if not _artifact_paths(artifacts.get("final")):
        issues.append("artifacts.final must name a file")
    if gates.get("recommendation_ready") is True:
        for category in RECOMMENDATION_ARTIFACTS:
            if not _artifact_paths(artifacts.get(category)):
                issues.append(f"recommendation_ready requires artifacts.{category}")

    for category, declared in artifacts.items():
        paths = _artifact_paths(declared)
        if not paths:
            issues.append(f"artifacts.{category} must contain file paths")
        for name in paths:
            relative = Path(name)
            target = (root / relative).resolve()
            if relative.is_absolute() or not target.is_relative_to(root):
                issues.append(f"artifact path escapes run directory: {name}")
            elif not target.is_file():
                issues.append(f"artifact file missing: {name}")
            elif gates.get("recommendation_ready") is True and target.stat().st_size == 0:
                issues.append(f"recommendation artifact is empty: {name}")
    return not issues, issues
