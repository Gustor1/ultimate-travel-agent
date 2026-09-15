# Using Travel Skills with Antigravity

Antigravity natively discovers and executes skills, agents, and workflows located in the `.agents/` folder of your active workspace.

---

## 1. How Antigravity Discovers Skills

When Antigravity opens a project containing `.agents/skills/`:
1. Each directory containing a `SKILL.md` with valid frontmatter is indexed.
2. The description, conditions of use, and tool requirements are loaded into the agent's capability registry.
3. When you submit a travel request, Antigravity matches the intent to `travel-orchestrator` or specialized skills automatically.

---

## 2. Invoking the Travel System in Antigravity

You can trigger travel planning in multiple ways:

### Option A: Complete Trip Planning (Recommended)
Copy the template from `examples/trip-brief-template.md`, fill it in, and prompt Antigravity:

```text
Follow workflow .agents/workflows/plan-complete-trip.md using this brief:
[Paste your filled brief here]
```

### Option B: Targeted Individual Tasks
You can also ask for specific individual travel components:

- **Transport Comparison**:
  `"Use transport-research skill to compare train vs flight options from Paris to Milan for next Friday."`

- **Accommodation Scouting**:
  `"Use accommodation-research skill to find 3 quiet boutique hotels in Lisbon's Alfama or Baixa neighborhoods."`

- **Itinerary Building**:
  `"Use itinerary-builder skill to create a 3-day balanced schedule in Florence based on these activities..."`

- **Safety & Visa Check**:
  `"Use travel-safety skill to check entry requirements and safety advisories for Costa Rica."`

---

## 3. The 5 Execution Waves

When orchestrating a full trip, Antigravity executes tasks in 5 structured waves:

```text
User Brief
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Wave 1: Parallel Research                                   │
│ (destination, transport, lodging, activities, safety)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Wave 2: Budget Consolidation                                │
│ (budget-analyst compiles line items & 15% safety buffer)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Wave 3: Itinerary Scheduling & Optimization                 │
│ (geographic clustering, transit buffers, rain backups)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Wave 4: Quality Control & Source Gate                       │
│ (verifies connections, opening hours, official sources)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Wave 5: Synthesis & Master Travel Dossier                   │
│ (delivers sourced plan with pre-booking verification links) │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Key Invariants

1. **Zero Automated Bookings**: Antigravity will never book tickets or initiate payments.
2. **Zero Credential Sharing**: Never enter credit cards, passport numbers, or account passwords.
3. **Official Sourcing**: All logistical claims must be confirmed by the traveler via the provided official links before travel.
