import os

code_to_add = '''
def validate_agent_file(agent_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single agent.md file against security invariants."""
    issues: List[str] = []
    if not agent_path.exists():
        return False, [f"File does not exist: {agent_path}"]

    try:
        content = agent_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    # Basic frontmatter parse
    if not content.startswith("---"):
        issues.append("Missing frontmatter opening '---'")
    parts = content.split("---", 2)
    fm = {}
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1])
            if not isinstance(fm, dict):
                issues.append("Frontmatter is not a valid YAML dictionary")
        except Exception as e:
            issues.append(f"Error parsing frontmatter YAML: {e}")
    else:
        issues.append("Malformed YAML frontmatter")

    agent_name = agent_path.parent.name
    internal_agents = ['budget-analyst', 'itinerary-optimizer', 'quality-controller', 'travel-orchestrator', 'mcp-skill-auditor']
    web_agents = ['destination-researcher', 'transport-planner', 'accommodation-researcher', 'activity-curator', 'local-discovery-agent', 'travel-preparation-agent', 'source-verification']

    tools = fm.get("tools", [])
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.strip("[]").split(",")]

    if agent_name in internal_agents:
        if "web_search" in tools or "browser" in tools:
            issues.append(f"Internal agent {agent_name} has web_search/browser in tools")
    elif agent_name in web_agents:
        if "<untrusted_web_content>" not in content:
            issues.append(f"Web agent {agent_name} missing <untrusted_web_content> defense")
        if "PII" not in content and "Personally Identifiable Information" not in content:
            issues.append(f"Web agent {agent_name} missing PII/personal keyword constraint")

    if "Agent Agent" in content:
        issues.append(f"Typo 'Agent Agent' found in {agent_name}")

    return (len(issues) == 0), issues


def validate_all_agents(agents_dir: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate all agents in the given or default agents directory."""
    if agents_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        agents_dir = repo_root / ".agents" / "agents"

    reports: Dict[str, List[str]] = {}
    all_passed = True
    
    expected_agents = [
        'budget-analyst', 'itinerary-optimizer', 'quality-controller', 'travel-orchestrator', 'mcp-skill-auditor',
        'destination-researcher', 'transport-planner', 'accommodation-researcher', 'activity-curator',
        'local-discovery-agent', 'travel-preparation-agent', 'source-verification'
    ]
    
    for expected in expected_agents:
        agent_dir = agents_dir / expected
        if not agent_dir.exists():
            reports[expected] = [f"Missing expected agent {expected}"]
            all_passed = False

    for agent_folder in sorted(agents_dir.iterdir()):
        if agent_folder.is_dir() and (agent_folder / "agent.md").exists():
            agent_md = agent_folder / "agent.md"
            passed, issues = validate_agent_file(agent_md)
            if issues:
                reports[agent_folder.name] = reports.get(agent_folder.name, []) + issues
            if not passed:
                all_passed = False

    return all_passed, reports
'''

with open(r'C:\Users\eliot\Desktop\ultimate-travel-agent\src\ultimate_travel_agent\validator.py', 'a', encoding='utf-8') as f:
    f.write('\n' + code_to_add)

print("validator.py updated")
