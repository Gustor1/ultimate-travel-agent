from pathlib import Path

from ultimate_travel_agent.validator import validate_all_agents


def test_source_verification_exists_and_secure():
    repo_root = Path(__file__).resolve().parent.parent
    sv_path = repo_root / ".agents" / "agents" / "source-verification" / "agent.md"
    assert sv_path.exists(), "source-verification agent.md does not exist"

    content = sv_path.read_text(encoding="utf-8")
    assert "<untrusted_web_content>" in content, "Missing untrusted_web_content defense"
    assert "PII" in content or "Personally Identifiable" in content, "Missing Zero-PII rule"


def test_all_agents_pass_validation():
    passed, reports = validate_all_agents()
    assert passed, f"Agent validation failed: {reports}"


def test_no_agent_agent_typos():
    repo_root = Path(__file__).resolve().parent.parent
    agents_dir = repo_root / ".agents" / "agents"
    for agent_folder in agents_dir.iterdir():
        if agent_folder.is_dir() and (agent_folder / "agent.md").exists():
            content = (agent_folder / "agent.md").read_text(encoding="utf-8")
            assert "Agent Agent" not in content, f"Typo 'Agent Agent' found in {agent_folder.name}"


def test_web_agents_defense():
    repo_root = Path(__file__).resolve().parent.parent
    agents_dir = repo_root / ".agents" / "agents"
    web_agents = [
        "destination-researcher",
        "transport-planner",
        "accommodation-researcher",
        "activity-curator",
        "local-discovery-agent",
        "travel-preparation-agent",
        "source-verification",
    ]
    for wa in web_agents:
        wa_path = agents_dir / wa / "agent.md"
        assert wa_path.exists(), f"Web agent {wa} missing"
        content = wa_path.read_text(encoding="utf-8")
        assert "<untrusted_web_content>" in content, f"Missing untrusted_web_content in {wa}"


def test_internal_agents_least_privilege():
    repo_root = Path(__file__).resolve().parent.parent
    agents_dir = repo_root / ".agents" / "agents"
    internal_agents = [
        "budget-analyst",
        "itinerary-optimizer",
        "quality-controller",
        "travel-orchestrator",
        "mcp-skill-auditor",
    ]
    for ia in internal_agents:
        ia_path = agents_dir / ia / "agent.md"
        if ia_path.exists():
            content = ia_path.read_text(encoding="utf-8")
            assert "web_search" not in content.lower() or (
                "tools:" in content.lower()
                and "web_search" not in content.lower().split("tools:")[1].split("---")[0]
            ), f"Internal agent {ia} has web_search"
            assert "browser" not in content.lower() or (
                "tools:" in content.lower()
                and "browser" not in content.lower().split("tools:")[1].split("---")[0]
            ), f"Internal agent {ia} has browser"
