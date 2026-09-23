from __future__ import annotations

from pathlib import Path

from evals.run_skill_evals import evaluate_cases, load_cases

ROOT = Path(__file__).resolve().parents[1]
TARGET_SKILLS = {
    "travel-orchestrator",
    "flight-search",
    "accommodation-research",
    "transport-research",
    "activity-curator",
    "source-verification",
    "travel-quality-control",
    "travel-safety",
    "mcp-skill-auditing",
}


def test_skill_eval_corpus_covers_trigger_boundaries_and_overlaps() -> None:
    cases = load_cases(ROOT / "evals" / "skill-routing-cases.yaml")
    assert len(cases) >= len(TARGET_SKILLS) * 4
    for skill in TARGET_SKILLS:
        categories = {
            case.category
            for case in cases
            if skill in case.focus_skills
        }
        assert categories == {"positive", "negative", "edge", "overlap"}, skill


def test_deterministic_skill_routing_eval_passes() -> None:
    failures = evaluate_cases(ROOT / "evals" / "skill-routing-cases.yaml")
    assert failures == []

