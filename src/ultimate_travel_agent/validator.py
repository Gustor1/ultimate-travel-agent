"""Skill quality validator ensuring compliance with project standards and safety invariants."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


def validate_skill_file(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single SKILL.md file against strict project standards.

    Checks:
    - Frontmatter YAML validity
    - name, description, conditions
    - Role, Inputs, Outputs
    - Tools (filesystem_read, etc.)
    - Fallback behavior without browser / web search
    - Source policy Tier 1 to Tier 6
    - Safety policy (no purchases, no reservations, no private data)
    - Booking / payment prohibition
    - Structured YAML output format
    - Example user request and expected output
    - Missing information and verification required handling
    """
    issues: List[str] = []
    if not skill_path.exists():
        return False, [f"File does not exist: {skill_path}"]

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    if len(content) < 400:
        issues.append(f"Content too short ({len(content)} chars)")

    # 1. YAML frontmatter
    if not content.startswith("---"):
        issues.append("Missing frontmatter opening '---'")
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues.append("Malformed YAML frontmatter")
    else:
        try:
            fm = yaml.safe_load(parts[1])
            if not isinstance(fm, dict):
                issues.append("Frontmatter is not a valid YAML dictionary")
            else:
                if not fm.get("name"):
                    issues.append("Missing 'name' in frontmatter")
                if not fm.get("description") or len(str(fm.get("description", ""))) < 10:
                    issues.append("Missing or too short 'description' in frontmatter")
                if not fm.get("conditions"):
                    issues.append("Missing 'conditions' in frontmatter")
        except Exception as e:
            issues.append(f"Error parsing frontmatter YAML: {e}")

    # 2. Structural sections
    content_lower = content.lower()
    if "role" not in content_lower:
        issues.append("Missing 'Role' section")
    if "inputs" not in content_lower:
        issues.append("Missing 'Inputs' section")
    if "outputs" not in content_lower:
        issues.append("Missing 'Outputs' section")
    if "tools" not in content_lower:
        issues.append("Missing 'Tools' section")

    # 3. Fallback behavior without web search / browser
    if "fallback" not in content_lower:
        issues.append("Missing 'Fallback' section")
    if "live research cannot be completed" not in content and "cannot be completed" not in content_lower:
        issues.append("Missing clear fallback statement when web research is unavailable")
    if "never invent live prices" not in content_lower and "never invent" not in content_lower:
        issues.append("Missing invariant: never invent live prices/availability")

    # 4. Source Policy (Tier 1 to Tier 6)
    if "source policy" not in content_lower and "sourcing policy" not in content_lower:
        issues.append("Missing 'Source Policy' section")
    if "tier 1" not in content_lower or "tier 6" not in content_lower:
        issues.append("Source policy must cover Tier 1 through Tier 6")

    # 5. Safety Policy & No booking/purchasing
    if "safety policy" not in content_lower:
        issues.append("Missing 'Safety Policy' section")
    if "never make purchases" not in content_lower:
        issues.append("Missing safety invariant: 'Never make purchases'")
    if "never make reservations" not in content_lower:
        issues.append("Missing safety invariant: 'Never make reservations'")
    if "personal or payment data" not in content_lower and "payment data" not in content_lower:
        issues.append("Missing safety invariant: never enter personal or payment data")

    # 6. Structured Output Format
    if "```yaml" not in content:
        issues.append("Missing structured ```yaml output format specification")
    for key in ["summary:", "recommendations:", "source_log:", "verification_required:", "risks:"]:
        if key not in content:
            issues.append(f"Structured output schema missing key: {key}")

    # 7. Example with User Request
    if "example" not in content_lower:
        issues.append("Missing 'Example' section")
    if "user request" not in content_lower and "user:" not in content_lower:
        issues.append("Missing explicit User Request in example")

    # 8. Handling missing info and verification
    if "missing_information" not in content:
        issues.append("Output format missing missing_information field")

    return (len(issues) == 0), issues


def validate_all_skills(skills_dir: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate all skills in the given or default skills directory."""
    if skills_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        skills_dir = repo_root / ".agents" / "skills"

    reports: Dict[str, List[str]] = {}
    all_passed = True

    for skill_folder in sorted(skills_dir.iterdir()):
        if skill_folder.is_dir() and (skill_folder / "SKILL.md").exists():
            skill_md = skill_folder / "SKILL.md"
            passed, issues = validate_skill_file(skill_md)
            reports[skill_folder.name] = issues
            if not passed:
                all_passed = False

    return all_passed, reports
