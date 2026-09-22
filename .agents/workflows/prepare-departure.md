# Workflow: Prepare Departure and Safety

## Purpose

Create an applicability-specific administrative, health, weather, insurance, medication, connectivity, and emergency checklist without collecting unnecessary PII or giving legal/medical clearance.

Read `../shared/compact-research-protocol.md`; return `compact-handoff/v2` action/blocker IDs.

## Agents Involved

- `travel-preparation-agent` using `travel-safety`
- `source-verification` for flagged critical claims

## Process

1. Build nationality/residency × jurisdiction × transit/border × date applicability using generic categories only.
2. Verify official entry, passport, visa/transit, customs, driving, advisory, health, vaccine, and medication-import claims. Label legal requirement, official recommendation, or precaution.
3. Assess severity × likelihood × traveler exposure for weather, environment, scams, remoteness, insurance, and evacuation; preserve high-impact blockers.
4. Record official emergency and consular contacts from current primary pages. Separate currency/connectivity convenience from safety requirements.
5. Generate departure-relative revalidation tasks; without current official access, keep claims unverified rather than issuing clearance.

## Deliverables

- Applicable preparation/action checklist
- Official evidence and emergency-contact IDs
- Risk, blocker, and revalidation schedule
