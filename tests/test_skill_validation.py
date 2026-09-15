"""Tests enforcing strict quality and safety standards on all travel skills."""

from pathlib import Path
from ultimate_travel_agent.validator import validate_all_skills, validate_skill_file


def test_all_13_skills_meet_quality_standard():
    """Verify that all 13 core skills pass the comprehensive quality validator."""
    passed, reports = validate_all_skills()
    assert passed, f"Skill validation failed on skills: {[k for k, v in reports.items() if v]}"


def test_packages_mirror_skills_meet_quality_standard():
    """Verify that skills in packages/travel-skills/skills also pass validation."""
    repo_root = Path(__file__).resolve().parent.parent
    pkg_skills_dir = repo_root / "packages" / "travel-skills" / "skills"
    passed, reports = validate_all_skills(pkg_skills_dir)
    assert passed, f"Packages skill validation failed: {[k for k, v in reports.items() if v]}"


def test_validator_catches_deficiencies(tmp_path):
    """Verify that the validator correctly detects incomplete skills."""
    bad_skill = tmp_path / "SKILL.md"
    bad_skill.write_text("name: bad-skill\nNo frontmatter\nNo safety policy", encoding="utf-8")
    passed, issues = validate_skill_file(bad_skill)
    assert not passed
    assert len(issues) > 0
