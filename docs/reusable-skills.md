# Reusable Travel Skills Pack Guide

This document describes how the Travel Skills Pack (`packages/travel-skills`) is organized, how it can be distributed and installed into any Antigravity-compatible workspace, and how each skill operates.

---

## 1. Overview

Antigravity agents automatically discover and activate skills placed in `.agents/skills/<skill-name>/SKILL.md`.

The **Travel Skills Pack** encapsulates the core travel reasoning protocols of `ultimate-travel-agent` into a modular, self-contained bundle that does not require installing the Python engine itself. Any project using Antigravity, Claude Code, or compatible agent frameworks can benefit from these guidelines.

---

## 2. Directory Layout

```text
packages/travel-skills/
├── README.md                      # Usage overview
├── manifest.json                  # Pack metadata & skill index
├── install.py                     # Standalone Python installer
├── uninstall.py                   # Standalone Python uninstaller
├── skills/                        # Packaged skill definitions
│   ├── travel-planning/
│   │   └── SKILL.md
│   ├── source-verification/
│   │   └── SKILL.md
│   ├── budget-validation/
│   │   └── SKILL.md
│   ├── travel-safety/
│   │   └── SKILL.md
│   ├── multi-agent-orchestration/
│   │   └── SKILL.md
│   └── mcp-skill-auditing/
│       └── SKILL.md
└── examples/
    ├── minimal-project/           # Minimal workspace with custom skill
    └── travel-project/            # Full workspace setup with sample prompts
```

---

## 3. The 6 Travel Skills

### 1. `travel-planning`
- **Focus:** Realistic scheduling, pacing, and crowd management.
- **Rules:**
  - Mandatory door-to-door transit buffers (30–45 min for trains, 90–120 min for domestic/EU flights, 180 min for long-haul).
  - Geographic clustering of attractions per day.
  - Sights cap (max 2-3 per day balanced, 1 per day relaxed).
  - Systematic rainy-day Plan B for any outdoor activity.
  - Zero automated booking: all reservations confirmed by user on official portals.

### 2. `source-verification`
- **Focus:** Provenance tracking and anti-hallucination.
- **Rules:**
  - Strict 6-tier reliability hierarchy: `official_verified` > `cross_checked` > `community_recommended` > `social_discovery_only` > `unverified` > `outdated`.
  - Social media trends must never be marked `confirmed`.
  - Enforces provenance metadata on all provider results.

### 3. `budget-validation`
- **Focus:** Deterministic financial formulas and cost overruns.
- **Rules:**
  - Mandatory safety contingency buffer: +10% to +12% (city trips) or +15% (road trips, remote expeditions).
  - Comprehensive 5-category accounting (`transport`, `accommodation`, `activities`, `meals`, `miscellaneous`).
  - Strict budget cap warnings.

### 4. `travel-safety`
- **Focus:** Health, diplomatic, and physical safety constraints.
- **Rules:**
  - Passport validity checks (3-6 months beyond return).
  - European Health Insurance Card (EHIC / CEAM) reminders.
  - Mandatory verified emergency numbers (112, 911, local police, national embassies).
  - Natural hazards warnings (sneaker waves, sudden storms, flash floods).

### 5. `multi-agent-orchestration`
- **Focus:** 5-wave DAG pipeline coordination.
- **Rules:**
  - Wave 1: Parallel exploration (flights, trains, stays, reviews, activities, preparation).
  - Wave 2: Budget consolidation.
  - Wave 3: Itinerary chronological optimization.
  - Wave 4: Quality control & security audit.
  - Wave 5: Final synthesis and dossier compilation.

### 6. `mcp-skill-auditing`
- **Focus:** Security auditing and external tool safety.
- **Rules:**
  - Read-only semantics enforcement (no shell execution, no destructive writes).
  - Strict fail-closed behavior for unconfigured live providers.
  - URL allowlisting for booking and government sites.
  - Anti-injection scanning on scraped or social media data.
  - Zero credential leakage in payloads or logs.

---

## 4. Installation & CLI Commands

### Installing into an External Project

```bash
# Using ultimate-travel-agent CLI
ultimate-travel-agent install-skills --target /path/to/my-agent-project

# Or with force overwrite
ultimate-travel-agent install-skills --target /path/to/my-agent-project --force

# Or using the portable python script
python packages/travel-skills/install.py --target /path/to/my-agent-project
```

### Listing Installed or Available Skills

```bash
ultimate-travel-agent list-skills
```

### Uninstalling from an External Project

```bash
# Removes only the 6 travel skills
ultimate-travel-agent uninstall-skills --target /path/to/my-agent-project

# Or using the portable script
python packages/travel-skills/uninstall.py --target /path/to/my-agent-project
```

---

## 5. Verification & Testing

The skills installation and uninstallation logic is covered by automated unit tests in `tests/test_skills_pack.py`, verifying:
- Non-destructive copying (preserves pre-existing project skills).
- Rejection of overwrite without `--force`.
- Full cleanup upon uninstallation.
- Cross-platform path resolution across Windows and Unix platforms.
