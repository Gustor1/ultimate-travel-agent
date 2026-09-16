"""Integration test suite verifying installation, tracking, and uninstallation in an isolated empty project."""

import json
import tempfile
from pathlib import Path

from ultimate_travel_agent.skills import (
    compute_file_sha256,
    get_install_manifest_path,
    install_pack_skills,
    load_install_manifest,
    uninstall_pack_skills,
)


def test_isolated_project_lifecycle():
    """Verify complete lifecycle in a new, completely isolated empty Antigravity project.

    Verifies all 11 requirements:
    1. Installation of skills alone.
    2. Installation of skills + agents + workflows.
    3. Presence of all 13 skills.
    4. Presence of all 12 agents.
    5. Presence of all 9 workflows.
    6. Creation and schema validity of .agents/.ultimate-travel-agent-install.json.
    7. Reinstallation without --force (collision protection).
    8. Reinstallation with --force (safe overwriting).
    9. Safe uninstallation preserving user-created skills, agents, workflows.
    10. Protection of user-modified files against accidental deletion.
    11. Clean directory removal of only empty travel folders.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_project = Path(tmpdir)

        # ---------------------------------------------------------
        # Step 1: Install skills alone
        # ---------------------------------------------------------
        res1 = install_pack_skills(target_dir=target_project, include_agents=False, include_workflows=False)
        assert len(res1["installed"]) >= 13
        manifest1 = load_install_manifest(target_project)
        assert manifest1 is not None
        assert manifest1["pack_name"] == "ultimate-travel-agent"
        assert len(manifest1["installed_skills"]) == 13
        assert len(manifest1["installed_agents"]) == 0
        assert len(manifest1["installed_workflows"]) == 0

        # ---------------------------------------------------------
        # Step 2: Install skills + agents + workflows
        # ---------------------------------------------------------
        res2 = install_pack_skills(
            target_dir=target_project,
            include_agents=True,
            include_workflows=True,
            force=False
        )
        assert res2["agents_count"] == 12
        assert res2["workflows_count"] == 9

        manifest2 = load_install_manifest(target_project)
        assert manifest2 is not None

        # ---------------------------------------------------------
        # Step 3: Check 13 skills present
        # ---------------------------------------------------------
        expected_skills = [
            "travel-orchestrator", "travel-web-research", "transport-research",
            "accommodation-research", "activity-curator", "local-discovery",
            "itinerary-builder", "budget-and-booking-checker", "travel-safety",
            "source-verification", "travel-quality-control", "multi-agent-orchestration",
            "mcp-skill-auditing"
        ]
        for s in expected_skills:
            skill_md = target_project / ".agents" / "skills" / s / "SKILL.md"
            assert skill_md.exists(), f"Missing skill: {s}"
            assert skill_md.stat().st_size > 300

        # ---------------------------------------------------------
        # Step 4: Check 12 agents present
        # ---------------------------------------------------------
        expected_agents = [
            "travel-orchestrator", "destination-researcher", "transport-planner",
            "accommodation-researcher", "activity-curator", "local-discovery-agent",
            "travel-preparation-agent", "budget-analyst", "itinerary-optimizer",
            "quality-controller", "mcp-skill-auditor"
        ]
        for a in expected_agents:
            agent_md = target_project / ".agents" / "agents" / a / "agent.md"
            assert agent_md.exists(), f"Missing agent: {a}"

        # ---------------------------------------------------------
        # Step 5: Check 9 workflows present
        # ---------------------------------------------------------
        expected_workflows = [
            "plan-complete-trip.md", "research-destination.md", "compare-transport.md",
            "find-accommodation.md", "curate-activities.md", "build-itinerary.md",
            "validate-trip.md", "prepare-departure.md", "audit-external-tool.md"
        ]
        for wf in expected_workflows:
            wf_file = target_project / ".agents" / "workflows" / wf
            assert wf_file.exists(), f"Missing workflow: {wf}"

        # ---------------------------------------------------------
        # Step 6: Manifest content & sha256 validity
        # ---------------------------------------------------------
        assert len(manifest2["files"]) >= 33
        for rel_path, meta in manifest2["files"].items():
            full_file = target_project / rel_path
            assert full_file.exists()
            assert meta["sha256"] == compute_file_sha256(full_file)

        # ---------------------------------------------------------
        # Step 7: Reinstall without --force (collision protection)
        # ---------------------------------------------------------
        test_file = target_project / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md"
        test_file.write_text("MODIFIED_BY_TEST", encoding="utf-8")
        res_no_force = install_pack_skills(target_project, include_agents=True, include_workflows=True, force=False)
        # Must skip the modified file
        assert test_file.read_text(encoding="utf-8") == "MODIFIED_BY_TEST"
        assert any("travel-orchestrator/SKILL.md" in s for s in res_no_force["skipped"])

        # ---------------------------------------------------------
        # Step 8: Reinstall with --force (safe overwriting)
        # ---------------------------------------------------------
        res_force = install_pack_skills(target_project, include_agents=True, include_workflows=True, force=True)
        assert test_file.read_text(encoding="utf-8") != "MODIFIED_BY_TEST"
        assert any("travel-orchestrator/SKILL.md" in o for o in res_force["overwritten"])

        # ---------------------------------------------------------
        # Step 9: Inject user-created custom skill, agent, and workflow
        # ---------------------------------------------------------
        user_skill_dir = target_project / ".agents" / "skills" / "my-custom-ski-touring"
        user_skill_dir.mkdir(parents=True, exist_ok=True)
        user_skill_file = user_skill_dir / "SKILL.md"
        user_skill_file.write_text("# My Personal Ski Touring Skill\nRole: Custom ski tour planner", encoding="utf-8")

        user_agent_dir = target_project / ".agents" / "agents" / "my-custom-ski-guide"
        user_agent_dir.mkdir(parents=True, exist_ok=True)
        user_agent_file = user_agent_dir / "agent.md"
        user_agent_file.write_text("# My Personal Ski Guide Agent", encoding="utf-8")

        user_workflow_file = target_project / ".agents" / "workflows" / "plan-ski-weekend.md"
        user_workflow_file.write_text("# Custom Ski Weekend Workflow", encoding="utf-8")

        # Also modify an installed travel skill to test modification protection
        target_transport_skill = target_project / ".agents" / "skills" / "transport-research" / "SKILL.md"
        target_transport_skill.write_text("USER_CUSTOMIZED_TRANSPORT_PROTOCOL", encoding="utf-8")

        # ---------------------------------------------------------
        # Step 10: Safe uninstallation (without --clean-modified or --force)
        # ---------------------------------------------------------
        un_res = uninstall_pack_skills(target_project, force=False, clean_modified=False)

        # Untouched travel files must be deleted
        assert not (target_project / ".agents" / "skills" / "travel-orchestrator").exists()
        assert not (target_project / ".agents" / "agents" / "travel-orchestrator").exists()
        assert not (target_project / ".agents" / "workflows" / "plan-complete-trip.md").exists()

        # Modified file MUST BE PRESERVED
        assert target_transport_skill.exists()
        assert target_transport_skill.read_text(encoding="utf-8") == "USER_CUSTOMIZED_TRANSPORT_PROTOCOL"
        assert any("transport-research/SKILL.md" in m for m in un_res["skipped_modified"])

        # User-created custom files MUST BE 100% PRESERVED
        assert user_skill_file.exists()
        assert user_agent_file.exists()
        assert user_workflow_file.exists()

        # Parent directories MUST BE PRESERVED because they contain user files
        assert (target_project / ".agents" / "skills").exists()
        assert (target_project / ".agents" / "agents").exists()
        assert (target_project / ".agents" / "workflows").exists()
        assert (target_project / ".agents").exists()

        # Manifest must reflect the remaining un-deleted modified file
        rem_manifest = load_install_manifest(target_project)
        assert rem_manifest is not None
        assert len(rem_manifest["files"]) == 1

        # ---------------------------------------------------------
        # Step 11: Final uninstallation with --clean-modified
        # ---------------------------------------------------------
        un_res2 = uninstall_pack_skills(target_project, clean_modified=True)
        assert not target_transport_skill.exists()
        assert not (target_project / ".agents" / "skills" / "transport-research").exists()

        # User custom files still perfectly intact!
        assert user_skill_file.exists()
        assert user_agent_file.exists()
        assert user_workflow_file.exists()

        # Manifest should now be fully cleaned up
        assert load_install_manifest(target_project) is None
