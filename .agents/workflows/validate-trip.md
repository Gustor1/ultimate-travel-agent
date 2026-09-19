# Workflow: Validate Trip Quality & Feasibility

## 1. Purpose
Conducts an objective quality audit against `TravelDossier v1` before delivery.
Verifies temporal feasibility, transit connection realism, budget arithmetic, source integrity, and constraint compliance.

## 2. Agents Involved
- `quality-controller` (Lead)
- `budget-analyst`
- `source-verification`
- `travel-quality-control` (Skill)

## 3. Input / Output Contracts
- **Input**: Full draft trip dossier (daily itinerary, transport routes, lodging, budget breakdown, safety plans).
- **Output**: Quality assurance report with validation score, detected flaws, blocking issues, and final publication approval.

## 4. Step-by-Step Execution Process

1. Validate the `TravelDossier v1` structure and unique claim/source IDs.
2. Reject missing or expired evidence references.
3. Recalculate typed cost totals from atomic components.
4. Check every transit connection, opening day, geographic cluster, pacing limit, and user constraint.
5. Reject social or community discoveries presented as operational facts without primary evidence.
6. Set `readiness.booking_ready: true` only when no critical blocker remains.

## 5. Deliverables
- Quality Assurance Audit Report
- List of Detected Issues & Corrections
- Validation Decision (Approved / Revisions Required)
