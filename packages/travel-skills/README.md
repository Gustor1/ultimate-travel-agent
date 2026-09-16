# Travel Skills Pack

A standalone, installable package of 13 battle-tested travel planning, source verification, financial budgeting, safety, and orchestration skills for Antigravity-compatible AI agents.

---

## 1. What is in the Pack?

The pack bundles 13 specialized skills located in `skills/`:

| Skill | Purpose |
| :--- | :--- |
| **ccommodation-research** | Investigates strategic neighborhoods and vets lodging options. |
| **ctivity-curator** | Curates cultural, historical, outdoor, and culinary activities. |
| **udget-and-booking-checker** | Consolidates trip expenditures and validates against budget. |
| **itinerary-builder** | Synthesizes destinations into chronological day-by-day itinerary. |
| **local-discovery** | Discovers off-the-beaten-path neighborhood spots. |
| **mcp-skill-auditing** | Security audit guidelines, URL allowlisting, prompt injection defenses. |
| **multi-agent-orchestration** | Coordinates multi-agent execution topologies. |
| **source-verification** | Rigorous verification hierarchy and provenance metadata. |
| **	ransport-research** | Researches multi-modal door-to-door transit options. |
| **	ravel-orchestrator** | Orchestrates end-to-end travel planning across 5 sequential waves. |
| **	ravel-quality-control** | Performs comprehensive quality assurance on travel dossiers. |
| **	ravel-safety** | Passport/visa validity checks, health prerequisites, emergency protocols. |
| **	ravel-web-research** | Broad destination research across official tourism portals. |

---

## 2. Installation into Any Antigravity Project

### Option A: Using the CLI
If you have `ultimate-travel-agent` installed:

```bash
# List available skills
ultimate-travel-agent list-skills

# Install skills into target project
ultimate-travel-agent install-skills --target /path/to/target-project

# Force overwrite of existing skills if updating
ultimate-travel-agent install-skills --target /path/to/target-project --force
```

### Option B: Direct Python Execution (Zero Dependencies)
You do not need any external packages installed—standard Python 3.10+ is all that is required:

```bash
# Preview what would be installed (dry run)
python packages/travel-skills/install.py --target /path/to/target-project --dry-run

# Run installation
python packages/travel-skills/install.py --target /path/to/target-project

# Overwrite existing skills
python packages/travel-skills/install.py --target /path/to/target-project --force
```

Skills are copied to:
```text
<target-project>/.agents/skills/
```

---

## 3. Uninstallation

To remove only the travel skills from a target project while preserving any other custom skills:

```bash
# Using CLI
ultimate-travel-agent uninstall-skills --target /path/to/target-project

# Or using Python script
python packages/travel-skills/uninstall.py --target /path/to/target-project
```

---

## 4. Guarantees & Safety

- **Non-Destructive by Default**: Never overwrites existing project skills unless `--force` is passed explicitly.
- **Selective Scope**: Only installs and removes skills listed in `manifest.json`.
- **Zero Third-Party Dependencies**: The installer uses only standard library (`shutil`, `pathlib`, `json`, `argparse`).
- **Cross-Platform**: Tested and working on Windows, macOS, and Linux.
- **Offline & Local**: Requires zero network access.
