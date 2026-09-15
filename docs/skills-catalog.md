# Travel Skills Catalog

Comprehensive reference catalog of all 13 core skills included in `ultimate-travel-agent`.
Each skill is standalone, local-first, open-source (MIT), and fully compatible with Antigravity.

---

| Skill Name | Role | Primary Tools | Output Deliverable |
|---|---|---|---|
| [`travel-orchestrator`](file:///.agents/skills/travel-orchestrator/SKILL.md) | Coordinates the 5-wave planning lifecycle and compiles master dossier | `filesystem_read`, `local_calculation` | Sourced Master Travel Dossier |
| [`travel-web-research`](file:///.agents/skills/travel-web-research/SKILL.md) | Researches destination climate, regional norms, and season windows | `web_search`, `browser`, `filesystem_read` | Destination Profile & Seasonal Matrix |
| [`transport-research`](file:///.agents/skills/transport-research/SKILL.md) | Compares door-to-door multi-modal transit (air, rail, road, ferry) | `web_search`, `browser`, `local_calculation` | Multi-Modal Transit Comparison Matrix |
| [`accommodation-research`](file:///.agents/skills/accommodation-research/SKILL.md) | Vets strategic neighborhoods and curates 3-5 lodging options | `web_search`, `browser`, `filesystem_read` | Vetted Lodging Shortlist |
| [`activity-curator`](file:///.agents/skills/activity-curator/SKILL.md) | Curates activities with anti-crowd tactics and rain backups | `web_search`, `browser`, `local_calculation` | Thematic Activity Catalog & Plan B |
| [`local-discovery`](file:///.agents/skills/local-discovery/SKILL.md) | Scouts authentic neighborhood eateries and hidden gems | `web_search`, `browser`, `filesystem_read` | Discovery Catalog (tagged Tier 4-6) |
| [`itinerary-builder`](file:///.agents/skills/itinerary-builder/SKILL.md) | Assembles chronological daily schedules with geographic clusters | `filesystem_read`, `local_calculation` | Chronological Day-by-Day Itinerary |
| [`budget-and-booking-checker`](file:///.agents/skills/budget-and-booking-checker/SKILL.md) | Audits expenses, adds 10-15% safety reserve, and lists booking deadlines | `filesystem_read`, `local_calculation` | Itemized Budget & Booking Schedule |
| [`travel-safety`](file:///.agents/skills/travel-safety/SKILL.md) | Reviews entry visas, health prerequisites, and emergency plans | `web_search`, `browser`, `filesystem_read` | Safety, Visa & Health Checklist |
| [`source-verification`](file:///.agents/skills/source-verification/SKILL.md) | Cross-checks claims against 6-tier sourcing hierarchy | `web_search`, `browser`, `filesystem_read` | Source Verification Audit Log |
| [`travel-quality-control`](file:///.agents/skills/travel-quality-control/SKILL.md) | Validates transit feasibility, budget arithmetic, and pacing | `filesystem_read`, `local_calculation` | Quality Gate Approval / Flaw Report |
| [`multi-agent-orchestration`](file:///.agents/skills/multi-agent-orchestration/SKILL.md) | Defines multi-agent wave execution topologies and data pipelines | `filesystem_read`, `local_calculation` | 5-Wave Multi-Agent Execution Plan |
| [`mcp-skill-auditing`](file:///.agents/skills/mcp-skill-auditing/SKILL.md) | Audits candidate external tools and MCP servers for security | `filesystem_read`, `web_search` | Tool Security & Privacy Audit Report |

---

## Universal Standards Guaranteed by Every Skill

1. **Standardized YAML Output Format**:
   Every skill returns a structured envelope containing `summary`, `recommendations`, `source_log`, `assumptions`, `missing_information`, `verification_required`, and `risks`.
2. **Safe Fallback Protocol**:
   When internet search is absent, every skill clearly declares the offline state and provides safe, un-hallucinated estimates with verification flags.
3. **Strict Safety Invariants**:
   Zero automated booking, zero purchasing, zero personal/payment data storage, zero paywall bypass.
