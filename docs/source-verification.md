# Source Verification & Sourcing Hierarchy

To protect travelers from outdated advice, tourist scams, and hallucinated logistics, `ultimate-travel-agent` enforces a strict 6-tier sourcing hierarchy across all skills and sub-agents.

---

## 1. The 6-Tier Sourcing Hierarchy

```text
┌──────────────┐
│    Tier 1    │  Official Sources: National governments, tourism ministries, city portals, embassies
├──────────────┤
│    Tier 2    │  Direct Operators: Rail networks (SNCF, JR, ÖBB), airlines, official museum box offices
├──────────────┤
│    Tier 3    │  Recognized Tourism Institutions: Regional tourism boards, UNESCO, public park authorities
├──────────────┤
│    Tier 4    │  Recognized Editorial Sources: Michelin Guide, Lonely Planet, reputable gastronomy critics
├──────────────┤
│    Tier 5    │  Community Reviews: TripAdvisor, Google Maps reviews, travel forum discussions
├──────────────┤
│    Tier 6    │  Social Media / Discovery Only: TikTok, Instagram, Xiaohongshu (RedNote), blogs
└──────────────┘
```

---

## 2. Rules Governing Each Tier

### Tier 1 & Tier 2 (Authoritative Logistical Truth)
- **Used for**: Visa requirements, passport validity, border rules, health mandates, train timetables, official ticket prices, and operating hours.
- **Requirement**: Must be referenced whenever confirming logistical feasibility.

### Tier 3 & Tier 4 (Editorial & Cultural Guidance)
- **Used for**: Cultural context, neighborhood overviews, curated highlights, architectural history, and seasonal crowd trends.
- **Rule**: Reliable for qualitative recommendations; opening hours and prices should still be corroborated against Tier 1/2 where feasible.

### Tier 5 (Community Feedback)
- **Used for**: Noise level assessments, recent crowd observations, staff helpfulness, and practical tips (e.g., "bring cash for lockers").
- **Rule**: Never use community reviews alone to confirm visa rules or train schedules. Filter out obvious sponsored content.

### Tier 6 (Social Discovery Only)
- **Used for**: Visual inspiration, emerging aesthetic spots, and hidden neighborhood corners.
- **Strict Rule**:
  > [!WARNING]
  > Social media content must **never** be presented as verified logistical information.
  > Any recommendation originating from Tier 6 must be tagged `social_discovery_only` and paired with a required verification step via Tier 1 or Tier 2.

---

## 3. Source Provenance Format

Every skill and agent produces a structured `source_log`:

```yaml
source_log:
  - name: "Japan National Tourism Organization (JNTO)"
    tier: 1
    url: "https://www.japan.travel"
    verified_aspects: ["Entry visa rules", "Tax-free shopping procedures"]
  - name: "East Japan Railway Company (JR East)"
    tier: 2
    url: "https://www.jreast.co.jp"
    verified_aspects: ["Shinkansen timetable", "Luggage dimension limits"]
  - name: "Neighborhood Food Blog"
    tier: 6
    url: "https://example.com/tokyo-eats"
    verified_aspects: ["Pintxos discovery suggestion"]
    verification_status: "Requires official opening hours verification"
```
