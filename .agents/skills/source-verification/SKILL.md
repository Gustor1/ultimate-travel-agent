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

4. **`social_discovery_only`**:
   - Content from viral social media platforms (TikTok, RedNote/Xiaohongshu, Instagram Reels).
   - Must be explicitly labeled to alert the user that opening times and prices are unverified.

5. **`unverified`**:
   - LLM estimates, extrapolations, or third-party claims lacking direct validation.

6. **`outdated`**:
   - Information known to precede recent policy, schedule, or price changes.
