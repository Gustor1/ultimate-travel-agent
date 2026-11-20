"""Score a user-facing trip plan against a golden output scenario.

Usage: python evals/run_output_evals.py evals/output-scenarios/london-6-days.yaml plan.md

The checks are deterministic text proxies for the skills' output contract. They catch
missing sections, forgotten entry requirements, and unlabeled prices; they do not judge
whether the recommendations are good.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    detail: str


def load_scenario(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("checks"), list):
        raise ValueError("output scenario must contain a checks list")
    return raw


def _run_check(check: dict[str, object], plan: str) -> CheckResult:
    check_id = str(check["id"])
    patterns = check.get("all_of")
    if isinstance(patterns, list):
        missing = [str(p) for p in patterns if not re.search(str(p), plan)]
        return CheckResult(check_id, not missing, "missing: " + ", ".join(missing) if missing else "ok")

    price_rule = check.get("price_lines_labeled")
    if isinstance(price_rule, dict):
        currency = re.compile(str(price_rule["currency"]))
        labels = re.compile(str(price_rule["labels"]))
        unlabeled = [
            line.strip()
            for line in plan.splitlines()
            if currency.search(line) and not labels.search(line)
        ]
        detail = "unlabeled: " + " | ".join(unlabeled[:5]) if unlabeled else "ok"
        return CheckResult(check_id, not unlabeled, detail)

    raise ValueError(f"check {check_id} has no supported rule")


def evaluate_plan(scenario_path: Path, plan: str) -> list[CheckResult]:
    scenario = load_scenario(scenario_path)
    checks = scenario["checks"]
    assert isinstance(checks, list)
    return [_run_check(check, plan) for check in checks]


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a trip plan against an output scenario")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    results = evaluate_plan(args.scenario, args.plan.read_text(encoding="utf-8"))
    for result in results:
        print(f"[{'OK' if result.passed else 'FAIL'}] {result.check_id}: {result.detail}")
    passed = sum(result.passed for result in results)
    print(f"{passed}/{len(results)} checks passed")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
