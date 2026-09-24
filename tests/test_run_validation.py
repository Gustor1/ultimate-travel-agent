"""Run-manifest validation at the boundary between research and final output."""

import os
import subprocess
import sys
from pathlib import Path

import yaml

from ultimate_travel_agent.run_validation import validate_run


def _write_run(root: Path, *, ready: bool = True) -> None:
    paths = {
        "final": "final.md",
        "sources": ["sources/transport.jsonl"],
        "research": ["research/transport.jsonl"],
        "decisions": ["decisions/route.jsonl"],
        "checks": ["checks/quality.jsonl"],
    }
    for name in (path for value in paths.values() for path in ([value] if isinstance(value, str) else value)):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("evidence\n", encoding="utf-8")
    manifest = {
        "schema": "travel-run/v1",
        "run_id": root.name,
        "status": "inspiration_mode",
        "gates": {
            "coverage_complete": ready,
            "evidence_sufficient": ready,
            "recommendation_ready": ready,
            "booking_ready": False,
        },
        "blockers": [],
        "artifacts": paths,
    }
    (root / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


def test_validate_run_accepts_consistent_manifest_and_artifacts(tmp_path: Path) -> None:
    run = tmp_path / "trip"
    run.mkdir()
    _write_run(run)

    passed, issues = validate_run(run)

    assert passed
    assert issues == []


def test_validate_run_rejects_false_recommendation_and_missing_evidence(tmp_path: Path) -> None:
    run = tmp_path / "trip"
    run.mkdir()
    _write_run(run)
    manifest_path = run / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["gates"]["evidence_sufficient"] = False
    del manifest["artifacts"]["checks"]
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    passed, issues = validate_run(run)

    assert not passed
    assert any("recommendation_ready requires evidence_sufficient" in issue for issue in issues)
    assert any("artifacts.checks" in issue for issue in issues)


def test_validate_run_rejects_missing_and_escaping_artifacts(tmp_path: Path) -> None:
    run = tmp_path / "trip"
    run.mkdir()
    _write_run(run)
    manifest_path = run / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["final"] = "missing.md"
    manifest["artifacts"]["sources"] = ["../outside.jsonl"]
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    passed, issues = validate_run(run)

    assert not passed
    assert any("artifact file missing: missing.md" in issue for issue in issues)
    assert any("artifact path escapes run directory" in issue for issue in issues)


def test_validate_run_cli_reports_failure(tmp_path: Path) -> None:
    run = tmp_path / "trip"
    run.mkdir()
    _write_run(run, ready=False)
    (run / "final.md").unlink()

    result = subprocess.run(
        [sys.executable, "-m", "ultimate_travel_agent.cli", "validate-run", str(run)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
    )

    assert result.returncode == 1
    assert "travel-run/v1: FAILED" in result.stdout
    assert "artifact file missing: final.md" in result.stdout
