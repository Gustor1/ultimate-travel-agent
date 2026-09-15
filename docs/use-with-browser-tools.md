# Using Travel Skills with Browser and Web Search Tools

The Travel Skills Pack is built to be **tool-adaptive**: it enhances its output when web tools are present, and degrades gracefully to safe local estimation when they are absent.

---

## 1. Tool Capabilities Overview

| Tool | Role in Travel Planning | Sourcing Level |
|---|---|---|
| `web_search` | Locates official tourism boards, transport timetables, and opening hours. | Tier 1, Tier 2, Tier 3 |
| `browser` | Reads rendered web pages, confirms timed-entry ticket availability and fare policies. | Tier 1, Tier 2 |
| `filesystem_read` | Ingests user trip briefs, cached local data, and regional templates. | Local |
| `local_calculation` | Computes transit durations, budget arithmetic, and currency conversions. | Local |

---

## 2. Behavior WITH Web Search & Browser Available

When your AI environment has active internet search and page-reading capabilities:
- **Live Timetable Lookups**: The agent checks current operator timetables and seasonal schedules.
- **Direct Official Links**: Extracts exact booking URLs from official carriers (e.g. Eurostar, ÖBB, SNCF).
- **Opening Hour Verification**: Verifies seasonal museum closures, renovation works, and holiday schedules.
- **Fresh Sourcing**: Tags all findings with source URLs and extraction timestamps.

---

## 3. Behavior WITHOUT Web Search & Browser (Safe Offline Fallback)

If web search or browser tools are disabled, unavailable, or restricted:

> [!IMPORTANT]
> **Strict Fallback Policy**: The AI must **never** hallucinate live fares, seat availability, or opening hours.

Instead, every skill executes the following standardized fallback protocol:
1. **Explicit Notice**: Declares that live research tools are unavailable and outputs are based solely on local data and general knowledge.
2. **Estimations Labeled**: Clearly tags all figures as `estimated` rather than `confirmed`.
3. **Verification Checklist**: Produces an exact list of items the user must manually check online prior to travel (e.g., "Check official museum site for current Tuesday closures").
4. **No Guarantees**: Never presents estimated fares as confirmed prices.

---

## 4. Security & Compliance Invariants

- **No Scraping Against Site Policies**: Skills respect site terms and public access standards.
- **No Login / Paywall Bypass**: Skills never attempt to circumvent authentication or subscription paywalls.
- **No Automated Form Submission**: Skills never submit personal traveler details on booking forms.
