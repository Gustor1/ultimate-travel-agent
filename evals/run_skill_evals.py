"""Run the dependency-free deterministic baseline for skill trigger evals."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    category: str
    focus_skills: frozenset[str]
    prompt: str
    expected: frozenset[str]


RULES: dict[str, tuple[tuple[str, ...], ...]] = {
    "travel-orchestrator": (
        (r"\bcomplete trip\b", r"\bend-to-end\b", r"\bplan (?:my |a )?trip\b", r"voyage complet", r"itin.raire complet"),
    ),
    "flight-search": (
        (r"\bflights?\b", r"\bairfare\b", r"\bvols?\b", r"billets? d.avion"),
    ),
    "accommodation-research": (
        (r"\bhotels?\b", r"\blodging\b", r"\baccommodation\b", r"h.bergement", r"\bauberge\b"),
    ),
    "transport-research": (
        (r"\btrains?\b", r"\brail\b", r"\bbus\b", r"\bferr(?:y|ies)\b", r"rental car", r"car rental", r"transport terrestre"),
    ),
    "activity-curator": (
        (r"\bmuseums?\b", r"\battractions?\b", r"\bactivities\b", r"things to do", r"activit.s", r"visites? culture"),
    ),
    "source-verification": (
        (r"\bverify\b", r"fact-check", r"source audit", r"stale claim", r"contradictory", r"v.rifie", r"sources? contradictoires"),
    ),
    "travel-quality-control": (
        (r"quality check", r"audit (?:my |the )?itinerary", r"itinerary (?:feasibility|is feasible)", r"validate (?:my |the )?trip", r"contr.le qualit", r"faisabilit.*itin.raire"),
    ),
    "travel-safety": (
        (r"\bvisa\b", r"entry requirements", r"vaccin", r"health rules", r"travel safety", r"weather advisory", r"s.curit.*voyage", r"formalit.s"),
    ),
    "mcp-skill-auditing": (
        (r"\bmcp\b", r"external (?:skill|api|connector|tool)", r"third-party (?:skill|api|connector|tool)"),
        (r"\baudit\b", r"security review", r"privacy review", r"permissions", r"s.curit", r"confidentialit"),
    ),
}

EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "flight-search": (r"(?:have|booked|chose) (?:a |the )?flight already",),
}


def route_prompt(prompt: str) -> frozenset[str]:
    selected: set[str] = set()
    for skill, required_groups in RULES.items():
        excluded = any(
            re.search(pattern, prompt, re.IGNORECASE)
            for pattern in EXCLUSIONS.get(skill, ())
        )
        if not excluded and all(any(re.search(pattern, prompt, re.IGNORECASE) for pattern in group) for group in required_groups):
            selected.add(skill)
    return frozenset(selected)


def load_cases(path: Path) -> list[EvalCase]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list):
        raise ValueError("skill eval corpus must contain a cases list")
    cases: list[EvalCase] = []
    for item in raw["cases"]:
        if not isinstance(item, dict):
            raise ValueError("each skill eval case must be an object")
        cases.append(
            EvalCase(
                case_id=str(item["id"]),
                category=str(item["category"]),
                focus_skills=frozenset(map(str, item["focus_skills"])),
                prompt=str(item["prompt"]),
                expected=frozenset(map(str, item["expected"])),
            )
        )
    return cases


def evaluate_cases(path: Path) -> list[str]:
    failures: list[str] = []
    for case in load_cases(path):
        actual = route_prompt(case.prompt)
        if actual != case.expected:
            failures.append(
                f"{case.case_id}: expected {sorted(case.expected)}, got {sorted(actual)}"
            )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic skill routing evals")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("skill-routing-cases.yaml"),
    )
    args = parser.parse_args()
    failures = evaluate_cases(args.path)
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Skill routing evals passed: {len(load_cases(args.path))} cases")


if __name__ == "__main__":
    main()
