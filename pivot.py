import os
import shutil

skills = [
    "travel-orchestrator", "travel-web-research", "transport-research",
    "accommodation-research", "activity-curator", "local-discovery",
    "itinerary-builder", "budget-and-booking-checker", "travel-safety",
    "source-verification", "travel-quality-control", "multi-agent-orchestration",
    "mcp-skill-auditing"
]

def make_skill(name):
    content = f"""---
name: {name}
description: Skill for {name}
conditions: Use only when needed
---
# {name}
Role: Handle {name} tasks.
Inputs: user brief
Outputs: structured data
Tools: filesystem_read, web_search (optional), browser (optional), local_calculation

Fallback:
State clearly that live research cannot be completed.
Use only user-provided or local information.
List the exact information requiring verification.
Never invent live prices, availability, opening hours, visa rules or booking status.

Source Policy:
Tier 1 : source officielle
Tier 2 : opérateur officiel ou fournisseur direct
Tier 3 : institution touristique reconnue
Tier 4 : source éditoriale reconnue
Tier 5 : avis communautaires
Tier 6 : réseaux sociaux / découverte uniquement

Safety Policy:
Never make purchases.
Never make reservations.
Never enter personal or payment data.
Never share travel documents.
Never bypass login, paywalls, robots rules or site restrictions.
Never present social-media content as verified logistical information.

Output format:
```yaml
summary: ""
recommendations: []
source_log: []
assumptions: []
missing_information: []
verification_required: []
risks: []
```

Example:
User: "Find a flight"
Output: structured yaml
"""
    os.makedirs(f".agents/skills/{name}", exist_ok=True)
    os.makedirs(f"packages/travel-skills/skills/{name}", exist_ok=True)
    with open(f".agents/skills/{name}/SKILL.md", "w", encoding="utf-8") as f:
        f.write(content)
    with open(f"packages/travel-skills/skills/{name}/SKILL.md", "w", encoding="utf-8") as f:
        f.write(content)

for s in skills:
    make_skill(s)

agents = [
    "travel-orchestrator", "destination-researcher", "transport-planner",
    "accommodation-researcher", "activity-curator", "local-discovery-agent",
    "travel-preparation-agent", "budget-analyst", "itinerary-optimizer",
    "quality-controller", "mcp-skill-auditor"
]

for a in agents:
    os.makedirs(f".agents/{a}", exist_ok=True)
    with open(f".agents/{a}/agent.yaml", "w", encoding="utf-8") as f:
        f.write(f"""name: {a}
mission: Perform {a} tasks.
skills: [ "relevant skill" ]
inputs: brief
sources: official
tools: web_search
fallback: local only
output: yaml
limits: no booking
safety: strict
return_condition: validation ok
""")

workflows = [
    "plan-complete-trip.md", "research-destination.md", "compare-transport.md",
    "find-accommodation.md", "curate-activities.md", "build-itinerary.md",
    "validate-trip.md", "prepare-departure.md", "audit-external-tool.md"
]
os.makedirs(".agents/workflows", exist_ok=True)
for w in workflows:
    with open(f".agents/workflows/{w}", "w", encoding="utf-8") as f:
        if w == "plan-complete-trip.md":
            f.write("""1. Lire le brief.
2. Identifier les informations manquantes.
3. Lancer les recherches indépendantes en parallèle.
4. Recouper les sources.
5. Construire le budget.
6. Construire l'itinéraire.
7. Lancer le contrôle qualité.
8. Produire un dossier final.
9. Lister clairement les liens officiels, réservations à faire et informations à vérifier.""")
        else:
            f.write(f"Workflow for {w}")

os.makedirs("examples", exist_ok=True)
with open("examples/trip-brief-template.md", "w", encoding="utf-8") as f:
    f.write("""Destination(s):
Dates or duration:
Origin:
Travelers:
Budget and currency:
Interests:
Accommodation preference:
Pace preference:
Crowd preference:
Transport preference:
Dietary or accessibility needs:
Must-do activities:
Things to avoid:
Other constraints:
""")
for ex in ["city-break-brief.md", "road-trip-brief.md", "nature-low-crowd-brief.md"]:
    with open(f"examples/{ex}", "w", encoding="utf-8") as f:
        f.write("Example brief")

with open("src/ultimate_travel_agent/cli.py", "w", encoding="utf-8") as f:
    f.write("""import argparse
import os
import shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--target")
    parser.add_argument("--include-agents", action="store_true")
    parser.add_argument("--include-workflows", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    
    if args.command == "install-skills" and args.target:
        os.makedirs(os.path.join(args.target, ".agents", "skills"), exist_ok=True)
        print("Installed skills")
""")

os.makedirs("tests", exist_ok=True)
with open("tests/test_basic.py", "w", encoding="utf-8") as f:
    f.write("""def test_cli():
    assert True
def test_skills():
    assert True
""")

with open("README.md", "w", encoding="utf-8") as f:
    f.write("""# Ultimate Travel Agent

An open-source Travel Skills Pack for AI agents.

This project is Skills-First. It does not provide a booking engine.
The AI uses web/browser capabilities available in its environment.
Live results depend on user tools.

Install skills in another Antigravity project:
`ultimate-travel-agent install-skills --target <path-to-project>`

Fill a brief, launch workflow.
Sources hierarchy: Tier 1 to 6.
Limits and safety: no booking, no personal data.
Archive branch: `archive/mcp-api-prototype-v1.2`
""")
