# Installing the Travel Skills Pack in Any Agent Project

The `ultimate-travel-agent` repository is designed with a **Skills-First** philosophy.
You can install this travel planning toolkit into any project whose agent host can consume local Markdown instructions. The files are host-neutral; capability and permission wiring remains platform-specific.

---

## 1. Quick Installation

From the root of this project (or after installing via pip):

```bash
# Install the 14 core travel skills into your target project:
python -m ultimate_travel_agent.cli install-skills --target /path/to/my-project
```

### Installing Sub-Agents and Workflows

To also install the 12 specialized agents and 9 end-to-end travel workflows:

```bash
python -m ultimate_travel_agent.cli install-skills \
  --target /path/to/my-project \
  --include-agents \
  --include-workflows
```

---

## 2. Command-Line Options

| Flag | Description |
|---|---|
| `--target <path>` | **Required.** The absolute or relative path to the destination project. |
| `--include-agents` | Copies the 12 specialized agents into `<target>/.agents/agents/`. |
| `--include-workflows` | Copies the 9 travel workflows into `<target>/.agents/workflows/`. |
| `--force` | Overwrites existing files in the target project. Without this flag, existing files are safely skipped. |

---

## 3. Directory Structure in the Target Project

After installation with all flags enabled, your target project will have:

```text
my-project/
└── .agents/
    ├── skills/
    │   ├── travel-orchestrator/SKILL.md
    │   ├── travel-web-research/SKILL.md
    │   ├── transport-research/SKILL.md
    │   ├── accommodation-research/SKILL.md
    │   ├── activity-curator/SKILL.md
    │   ├── local-discovery/SKILL.md
    │   ├── itinerary-builder/SKILL.md
    │   ├── budget-and-booking-checker/SKILL.md
    │   ├── travel-safety/SKILL.md
    │   ├── source-verification/SKILL.md
    │   ├── travel-quality-control/SKILL.md
    │   ├── multi-agent-orchestration/SKILL.md
    │   └── mcp-skill-auditing/SKILL.md
    ├── agents/
    │   ├── travel-orchestrator/agent.md
    │   ├── destination-researcher/agent.md
    │   ├── transport-planner/agent.md
    │   ├── accommodation-researcher/agent.md
    │   ├── activity-curator/agent.md
    │   ├── local-discovery-agent/agent.md
    │   ├── travel-preparation-agent/agent.md
    │   ├── budget-analyst/agent.md
    │   ├── itinerary-optimizer/agent.md
│   ├── quality-controller/agent.md
│   ├── source-verification/agent.md
│   └── mcp-skill-auditor/agent.md
    └── workflows/
        ├── plan-complete-trip.md
        ├── research-destination.md
        ├── compare-transport.md
        ├── find-accommodation.md
        ├── curate-activities.md
        ├── build-itinerary.md
        ├── validate-trip.md
        ├── prepare-departure.md
        └── audit-external-tool.md
```

---

## 4. Safe Uninstallation

If you ever wish to remove the travel skills from your project:

```bash
python -m ultimate_travel_agent.cli uninstall-skills --target /path/to/my-project
```

This removes only manifest-tracked files. Modified files remain unless explicitly cleaned. Files replaced with `--force` are restored from local backups. A missing or malformed manifest stops removal.
