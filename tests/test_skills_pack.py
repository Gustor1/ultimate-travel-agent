"""Unit tests for Reusable Travel Skills Pack and installation workflows."""

import json
from pathlib import Path
import pytest
from ultimate_travel_agent.skills import (
    find_pack_root,
    get_manifest,
    install_pack_skills,
    list_available_skills,
    uninstall_pack_skills,
)


def test_manifest_structure() -> None:
    """Check that manifest.json exists, is valid, and registers all 6 travel skills."""
    pack_root = find_pack_root()
    manifest = get_manifest(pack_root)

    assert manifest["name"] == "travel-skills"
    assert manifest["version"] == "1.0.0"

    skill_names = [s["name"] for s in manifest["skills"]]
    expected = [
        "travel-planning",
        "source-verification",
        "budget-validation",
        "travel-safety",
        "multi-agent-orchestration",
        "mcp-skill-auditing",
    ]
    for exp in expected:
        assert exp in skill_names

    # Check that all SKILL.md files actually exist in pack
    skills_dir = pack_root / "skills"
    for s in manifest["skills"]:
        skill_file = skills_dir / s["name"] / "SKILL.md"
        assert skill_file.exists(), f"Missing file: {skill_file}"
        content = skill_file.read_text(encoding="utf-8")
        assert f"name: {s['name']}" in content


def test_list_available_skills() -> None:
    """Test list_available_skills returns all 6 skills."""
    skills = list_available_skills()
    assert len(skills) == 6
    names = {s["name"] for s in skills}
    assert "travel-planning" in names
    assert "mcp-skill-auditing" in names


def test_install_skills_fresh(tmp_path: Path) -> None:
    """Test installing skills into a fresh directory."""
    installed, skipped, overwritten = install_pack_skills(target_dir=tmp_path)
    assert len(installed) == 6
    assert len(skipped) == 0
    assert len(overwritten) == 0

    dest_skills_dir = tmp_path / ".agents" / "skills"
    assert dest_skills_dir.exists()
    for name in [
        "travel-planning",
        "source-verification",
        "budget-validation",
        "travel-safety",
        "multi-agent-orchestration",
        "mcp-skill-auditing",
    ]:
        skill_file = dest_skills_dir / name / "SKILL.md"
        assert skill_file.exists()


def test_install_skills_prevent_overwrite(tmp_path: Path) -> None:
    """Test that existing skills are not overwritten unless force=True."""
    # First install
    install_pack_skills(target_dir=tmp_path)

    # Modify one skill in target
    target_file = tmp_path / ".agents" / "skills" / "travel-planning" / "SKILL.md"
    target_file.write_text("CUSTOM USER MODIFICATIONS", encoding="utf-8")

    # Second install without force
    installed, skipped, overwritten = install_pack_skills(target_dir=tmp_path, force=False)
    assert len(installed) == 0
    assert "travel-planning" in skipped
    assert target_file.read_text(encoding="utf-8") == "CUSTOM USER MODIFICATIONS"

    # Third install with force
    installed, skipped, overwritten = install_pack_skills(target_dir=tmp_path, force=True)
    assert "travel-planning" in overwritten
    assert "CUSTOM USER MODIFICATIONS" not in target_file.read_text(encoding="utf-8")


def test_install_preserves_unrelated_skills(tmp_path: Path) -> None:
    """Test that installing pack skills leaves pre-existing custom skills untouched."""
    custom_skill_dir = tmp_path / ".agents" / "skills" / "custom-company-policy"
    custom_skill_dir.mkdir(parents=True)
    custom_file = custom_skill_dir / "SKILL.md"
    custom_file.write_text("Custom internal instructions", encoding="utf-8")

    install_pack_skills(target_dir=tmp_path)

    assert custom_file.exists()
    assert custom_file.read_text(encoding="utf-8") == "Custom internal instructions"


def test_uninstall_skills(tmp_path: Path) -> None:
    """Test uninstalling pack skills leaves other skills intact."""
    install_pack_skills(target_dir=tmp_path)

    # Create another skill
    custom_skill_dir = tmp_path / ".agents" / "skills" / "keep-me"
    custom_skill_dir.mkdir(parents=True)
    (custom_skill_dir / "SKILL.md").write_text("Keep me", encoding="utf-8")

    # Uninstall
    removed, not_found = uninstall_pack_skills(target_dir=tmp_path)
    assert len(removed) == 6
    assert (custom_skill_dir / "SKILL.md").exists()

    # Re-uninstalling reports not_found
    removed2, not_found2 = uninstall_pack_skills(target_dir=tmp_path)
    assert len(removed2) == 0
    assert len(not_found2) == 6


def test_install_dry_run(tmp_path: Path) -> None:
    """Test that dry-run creates no files."""
    installed, skipped, overwritten = install_pack_skills(target_dir=tmp_path, dry_run=True)
    assert len(installed) == 6
    dest_skills_dir = tmp_path / ".agents" / "skills"
    assert not dest_skills_dir.exists()
