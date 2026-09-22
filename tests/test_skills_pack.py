"""Comprehensive test suite for Phase 11 Skills-First Pivot."""

import argparse
import os
import tempfile
from pathlib import Path

import yaml

from ultimate_travel_agent.cli import get_base_dir, install_skills, uninstall_skills


def test_install_in_temp_project():
    """Verify that install-skills copies skills, agents, and workflows into a target project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        args = argparse.Namespace(
            command="install-skills",
            target=str(target_path),
            include_agents=True,
            include_workflows=True,
            force=False,
        )
        install_skills(args)

        # 1. Check all 14 skills are installed
        skills_dest = target_path / ".agents" / "skills"
        assert skills_dest.exists()
        expected_skills = [
            "travel-orchestrator",
            "travel-web-research",
            "transport-research",
            "accommodation-research",
            "activity-curator",
            "local-discovery",
            "itinerary-builder",
            "budget-and-booking-checker",
            "travel-safety",
            "source-verification",
            "travel-quality-control",
            "multi-agent-orchestration",
            "mcp-skill-auditing",
            "flight-search",
        ]
        for skill in expected_skills:
            skill_file = skills_dest / skill / "SKILL.md"
            assert skill_file.exists(), f"Missing skill in target: {skill}"
            assert skill_file.stat().st_size > 100

        # 2. Check workflows are installed
        workflows_dest = target_path / ".agents" / "workflows"
        assert workflows_dest.exists()
        assert (workflows_dest / "plan-complete-trip.md").exists()
        assert (workflows_dest / "compare-transport.md").exists()
        assert (workflows_dest / "find-accommodation.md").exists()

        # 3. Check agents are installed
        agents_dest = target_path / ".agents" / "agents"
        assert agents_dest.exists()
        assert (agents_dest / "travel-orchestrator" / "agent.md").exists()
        assert (agents_dest / "quality-controller" / "agent.md").exists()


def test_no_overwrite_without_force():
    """Verify that existing files are preserved unless --force is specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        args = argparse.Namespace(
            command="install-skills",
            target=str(target_path),
            include_agents=False,
            include_workflows=False,
            force=False,
        )
        install_skills(args)

        skill_file = target_path / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md"
        assert skill_file.exists()
        skill_file.write_text("CUSTOM_USER_CONTENT", encoding="utf-8")

        # Reinstall without force: file must NOT change
        install_skills(args)
        assert skill_file.read_text(encoding="utf-8") == "CUSTOM_USER_CONTENT"

        # Reinstall with force: file MUST be overwritten
        args.force = True
        install_skills(args)
        assert skill_file.read_text(encoding="utf-8") != "CUSTOM_USER_CONTENT"


def test_uninstall():
    """Verify that uninstall-skills removes installed components cleanly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        args = argparse.Namespace(
            command="install-skills",
            target=str(target_path),
            include_agents=True,
            include_workflows=True,
            force=False,
        )
        install_skills(args)

        assert (target_path / ".agents" / "skills").exists()
        assert (target_path / ".agents" / "agents").exists()
        assert (target_path / ".agents" / "workflows").exists()

        un_args = argparse.Namespace(
            command="uninstall-skills",
            target=str(target_path),
        )
        uninstall_skills(un_args)

        assert not (target_path / ".agents" / "skills").exists()
        assert not (target_path / ".agents" / "agents").exists()
        assert not (target_path / ".agents" / "workflows").exists()


def test_all_14_skills_frontmatter_and_policies():
    """Verify that all 14 skills adhere to the mandatory schema, frontmatter, and safety invariants."""
    base_dir = get_base_dir()
    skills_dir = base_dir / ".agents" / "skills"

    expected_skills = [
        "travel-orchestrator",
        "travel-web-research",
        "transport-research",
        "accommodation-research",
        "activity-curator",
        "local-discovery",
        "itinerary-builder",
        "budget-and-booking-checker",
        "travel-safety",
        "source-verification",
        "travel-quality-control",
        "multi-agent-orchestration",
        "mcp-skill-auditing",
        "flight-search",
    ]

    for skill_name in expected_skills:
        skill_path = skills_dir / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Skill file does not exist: {skill_path}"

        content = skill_path.read_text(encoding="utf-8")
        assert len(content) > 500, f"Skill content too brief: {skill_name}"

        # Frontmatter validation
        assert content.startswith("---"), f"Missing frontmatter start in {skill_name}"
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"Malformed frontmatter in {skill_name}"
        fm = yaml.safe_load(parts[1])
        assert fm["name"] == skill_name
        assert "description" in fm and len(fm["description"]) > 15
        assert "conditions" not in fm

        # Universal policy and the handoff schema are inherited from one shared contract.
        assert "compact-research-protocol.md" in content
        assert "compact-handoff/v2" in content
        assert "schema: compact-handoff" not in content
        assert "source_log:" not in content


def test_all_9_workflows_detailed():
    """Verify that all 9 workflows exist and contain detailed process descriptions."""
    base_dir = get_base_dir()
    wf_dir = base_dir / ".agents" / "workflows"

    expected_workflows = [
        "plan-complete-trip.md",
        "research-destination.md",
        "compare-transport.md",
        "find-accommodation.md",
        "curate-activities.md",
        "build-itinerary.md",
        "validate-trip.md",
        "prepare-departure.md",
        "audit-external-tool.md",
    ]

    for wf in expected_workflows:
        wf_path = wf_dir / wf
        assert wf_path.exists(), f"Missing workflow: {wf}"
        content = wf_path.read_text(encoding="utf-8")
        assert len(content) > 300, f"Workflow content too short: {wf}"
        assert "Purpose" in content
        assert "Agents Involved" in content
        assert "Deliverables" in content


def test_bilingual_brief_templates_are_substantial():
    """Verify that the two user-facing brief templates remain useful."""
    base_dir = get_base_dir()
    ex_dir = base_dir / "examples"

    expected_briefs = [
        "trip-brief-template.md",
        "trip-brief-template.fr.md",
    ]

    for b in expected_briefs:
        b_path = ex_dir / b
        assert b_path.exists(), f"Missing example brief: {b}"
        content = b_path.read_text(encoding="utf-8")
        assert len(content) > 300, f"Brief content too short: {b}"


def test_all_12_agents_skills_first():
    """Verify that all 12 sub-agents in .agents/agents are configured for Skills-First."""
    base_dir = get_base_dir()
    agents_dir = base_dir / ".agents" / "agents"

    expected_agents = [
        "travel-orchestrator",
        "destination-researcher",
        "transport-planner",
        "accommodation-researcher",
        "activity-curator",
        "local-discovery-agent",
        "travel-preparation-agent",
        "budget-analyst",
        "itinerary-optimizer",
        "quality-controller",
        "mcp-skill-auditor",
        "source-verification",
    ]

    for agent_id in expected_agents:
        agent_file = agents_dir / agent_id / "agent.md"
        assert agent_file.exists(), f"Missing agent definition: {agent_id}"
        content = agent_file.read_text(encoding="utf-8")
        assert "Skills-First" in content or "skills" in content.lower()
        # Ensure retired Provider Hub is not claimed as an active cloud component
        assert "Provider Hub Integration" not in content


def test_documentation_guides_exist():
    """Verify that all Phase 11 required documentation guides exist and have substance."""
    base_dir = get_base_dir()
    docs_dir = base_dir / "docs"

    expected_docs = [
        "install-in-any-project.md",
        "source-verification.md",
        "skills-catalog.md",
        "token-efficiency.md",
    ]

    for doc in expected_docs:
        doc_path = docs_dir / doc
        assert doc_path.exists(), f"Missing documentation file: {doc}"
        assert doc_path.stat().st_size > 200, f"Doc too brief: {doc}"

def test_no_mcp_api_components_in_main():
    """Verify that cloud/server MCP components, Docker, and deployment files are retired from main."""
    base_dir = get_base_dir()
    src_dir = base_dir / "src" / "ultimate_travel_agent"

    # Retired components
    assert not (src_dir / "mcp").exists()
    assert not (src_dir / "integrations").exists()
    assert not (src_dir / "web").exists()
    assert not (base_dir / "docker-compose.yml").exists()
    assert not (base_dir / "Dockerfile").exists()
    assert not (base_dir / "deployment").exists()
    assert not (base_dir / ".dockerignore").exists()
    assert not (base_dir / ".env.example").exists()
    assert not (base_dir / "railway.json").exists()
    assert not (base_dir / "pivot.py").exists()

    # Phase 15 cleanup: retired legacy directories & files
    assert not (base_dir / "archive").exists()
    assert not (base_dir / "config").exists()
    assert not (base_dir / "PROMPT_ANTIGRAVITY_PHASE_11_SKILLS_FIRST_PIVOT.md").exists()
    assert not (base_dir / "ULTIMATE_TRAVEL_AGENT_MASTER_PLAN.md").exists()
    assert not (base_dir / "research").exists()
    assert not (base_dir / "data").exists()
    assert not (base_dir / "examples" / "city-trip").exists()
    assert not (base_dir / "examples" / "road-trip").exists()

    # Pre-pivot archives and generated mirrors do not belong in the active pack.
    assert not (base_dir / "docs" / "history").exists()
    assert not (base_dir / "packages").exists()


def test_no_secrets_and_personal_paths():
    """Verify zero sensitive API keys and zero personal Windows filepaths in repository."""
    base_dir = get_base_dir()

    for root, _dirs, files in os.walk(base_dir):
        if any(
            ignored in root for ignored in [".git", "node_modules", "__pycache__", ".pytest_cache"]
        ):
            continue
        for file in files:
            if not file.endswith((".py", ".md", ".json", ".yaml", ".yml")):
                continue
            path = Path(root) / file
            try:
                content = path.read_text(encoding="utf-8")
                assert "c:\\Users\\eliot" not in content.lower(), f"Personal path in {path}"
                # Ensure no live API tokens
                if "api_key" in content.lower():
                    assert (
                        "mock" in content.lower()
                        or "example" in content.lower()
                        or "your_" in content.lower()
                        or "without" in content.lower()
                        or "keyless" in content.lower()
                    ), f"Potential exposed secret in {path}"
            except UnicodeDecodeError:
                pass
