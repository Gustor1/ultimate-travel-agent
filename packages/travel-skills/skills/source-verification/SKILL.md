---
name: source-verification
description: Protocols for grading information reliability, verifying travel facts, cross-referencing sources, and tagging verification levels.
---

# Source Verification Skill

## Overview
This skill establishes strict evaluation criteria for every piece of travel data (fares, timetables, visa rules, opening hours, lodging reviews).

## Verification Hierarchy

1. **`official_verified`**:
   - Primary government websites (ministries of foreign affairs, consulates, immigration).
   - Official national railway operators (SNCF, Renfe, DB, JR).
   - Official monument and museum box offices (e.g. sagradafamilia.org, louvre.fr).
   - Direct airlines and national park authorities.

2. **`cross_checked`**:
   - Reputable, established travel guidebooks (Lonely Planet, Le Guide du Routard, Michelin Green Guide).
   - Official municipal tourism boards.
   - Independent confirmation by at least 2 reputable sources.

3. **`community_recommended`**:
   - High-volume travel community consensus (TripAdvisor top-ranked with recent reviews, Reddit travel forums).
   - Wikivoyage destination articles (`WikivoyageProvider`): rich editorial knowledge, but prices, operating hours, and visas remain community estimates.
   - Quality controller rule: Never permit `price_status: confirmed` on `community_recommended` guide entries.

4. **`social_discovery_only`**:
   - Content from viral social media platforms (TikTok, RedNote/Xiaohongshu, Instagram Reels).
   - Must be explicitly labeled to alert the user that opening times and prices are unverified.
   - Quality controller rule: Never permit `price_status: confirmed` on `social_discovery_only` items.

5. **`unverified`**:
   - LLM estimates, extrapolations, or third-party claims lacking direct validation.

6. **`outdated`**:
   - Information known to precede recent policy, schedule, or price changes.

## Provider Hub V1.2 & Phase 10 Provenance Protocol
Every item produced by a Provider Hub adapter or keyless integration must return standard provenance metadata:
```yaml
provider: provider_name
category: flight | train | hotel | activity | review | map | weather | currency | guide | social
mode: offline | mock | live
retrieved_at: <ISO timestamp>
source_url: <Official booking/reference URL>
attribution: <Required open license / data attribution string>
verification_level: official_verified | cross_checked | community_recommended | social_discovery_only | unverified
cache_status: hit | miss | stale
result_status: live | unavailable | needs_verification
currency: <3-letter ISO code or null>
price_status: confirmed | estimated | needs_verification
availability_status: live | estimated | unavailable | unknown
requires_booking_verification: true | false
```
All recommendations remain subject to manual booking verification on official partner channels. Direct transactions or financial payments are strictly prohibited.

