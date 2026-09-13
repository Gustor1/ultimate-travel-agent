# Travel Skills Pack

A standalone, installable package of 6 battle-tested travel planning, source verification, financial budgeting, safety, and orchestration skills for Antigravity-compatible AI agents.

---

## 1. What is in the Pack?

The pack bundles 6 specialized skills located in `skills/`:

| Skill | Purpose |
| :--- | :--- |
| **`travel-planning`** | Best practices for realistic pacing, door-to-door transit buffers, geographic clustering, crowd avoidance ("moins de monde"), and weather Plan B contingencies. |
| **`source-verification`** | Rigorous verification hierarchy (`official_verified`, `cross_checked`, `community_recommended`, `social_discovery_only`, `unverified`) and provenance metadata. |
| **`budget-validation`** | Financial rules, multi-currency conversions, +10% to +15% safety contingency reserve calculation, and budget cap enforcement. |
| **`travel-safety`** | Passport/visa validity checks, European Health Insurance Card (EHIC) reminders, local emergency contacts (112, 911, embassies), and hazard warnings. |
| **`multi-agent-orchestration`**| 5-wave DAG pipeline coordination pattern preventing hallucination compounding and context window exhaustion. |
| **`mcp-skill-auditing`** | Security audit guidelines, URL allowlisting, prompt injection defenses, and strict zero-booking assurance. |

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
