"""Fail-closed and reversibility tests for the pack installer."""

import json
import tempfile
from pathlib import Path

import pytest

from ultimate_travel_agent import __version__
from ultimate_travel_agent.skills import (
    ManifestError,
    get_install_manifest_path,
    install_pack_skills,
    uninstall_pack_skills,
)


@pytest.fixture
def isolated_tmp_path():
    with tempfile.TemporaryDirectory() as directory:
        yield Path(directory)


def test_missing_manifest_never_triggers_guessed_deletion(isolated_tmp_path: Path):
    tmp_path = isolated_tmp_path
    user_file = tmp_path / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md"
    user_file.parent.mkdir(parents=True)
    user_file.write_text("user-owned", encoding="utf-8")

    result = uninstall_pack_skills(tmp_path)

    assert user_file.read_text(encoding="utf-8") == "user-owned"
    assert result["removed"] == []
    assert result["errors"]


@pytest.mark.parametrize(
    "manifest_payload",
    [
        "not-json",
        json.dumps({"files": {"../outside.txt": {"sha256": "deadbeef"}}}),
        json.dumps({"files": {".agents/skill.md": {}}}),
    ],
)
def test_invalid_manifest_fails_closed(isolated_tmp_path: Path, manifest_payload: str):
    tmp_path = isolated_tmp_path
    tracked_file = tmp_path / ".agents" / "skill.md"
    tracked_file.parent.mkdir(parents=True)
    tracked_file.write_text("preserve", encoding="utf-8")
    get_install_manifest_path(tmp_path).write_text(manifest_payload, encoding="utf-8")

    with pytest.raises(ManifestError):
        uninstall_pack_skills(tmp_path)

    assert tracked_file.read_text(encoding="utf-8") == "preserve"


def test_explicit_pack_root_is_used(isolated_tmp_path: Path):
    tmp_path = isolated_tmp_path
    bundle = tmp_path / "bundle"
    skill = bundle / "skills" / "custom" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Custom bundle skill", encoding="utf-8")
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_schema": 1,
                "name": "custom",
                "version": __version__,
                "skills": [{"name": "custom", "path": "skills/custom/SKILL.md"}],
                "agents": [],
                "workflows": [],
            }
        ),
        encoding="utf-8",
    )
    target = tmp_path / "target"

    result = install_pack_skills(target, pack_root=bundle)

    installed = target / ".agents" / "skills" / "custom" / "SKILL.md"
    assert result["skills_count"] == 1
    assert installed.read_text(encoding="utf-8") == "# Custom bundle skill"


def test_force_overwrite_is_restored_on_uninstall(isolated_tmp_path: Path):
    tmp_path = isolated_tmp_path
    destination = tmp_path / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("user version", encoding="utf-8")

    install_pack_skills(tmp_path, force=True)
    assert destination.read_text(encoding="utf-8") != "user version"

    result = uninstall_pack_skills(tmp_path)

    assert destination.read_text(encoding="utf-8") == "user version"
    assert any("travel-orchestrator/SKILL.md" in item for item in result["restored"])
