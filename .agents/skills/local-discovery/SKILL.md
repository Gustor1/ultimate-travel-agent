---
name: local-discovery
description: Skill for local-discovery
conditions: Use only when needed
---
# local-discovery
Role: Handle local-discovery tasks.
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
