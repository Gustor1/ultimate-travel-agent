# Workflow: Validate Trip Quality & Feasibility

## 1. Purpose
Conducts an objective, multi-point quality assurance audit on the entire drafted travel dossier before delivering it to the traveler.
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
1. **Temporal & Transit Audit**: Check every transit connection. Flag impossible transfers (e.g. <45 mins between disparate terminals) or excessive driving days (>5 hours).
2. **Operating Hours & Days Check**: Verify that scheduled attractions are open on the assigned calendar days (e.g. verifying Monday museum closures).
3. **Budget Consistency Audit**: Re-calculate all line items, confirm currency conversion consistency, and verify the mandatory 10-15% safety reserve.
4. **Source Provenance Verification**: Ensure that no unverified social media claims or AI hallucinations are presented as logistical facts.
5. **Constraint Compliance**: Check that user dietary restrictions, mobility needs, and pacing preferences are strictly honored.

## 5. Deliverables
- Quality Assurance Audit Report
- List of Detected Issues & Corrections
- Validation Decision (Approved / Revisions Required)
