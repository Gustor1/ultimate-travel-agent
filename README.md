# Ultimate Travel Agent

An open-source Travel Skills Pack for AI agents.

## Skills-First Approach

This project is strictly **Skills-First**. It does **not** provide a booking engine, and it does **not** provide its own web scraping infrastructure or complex APIs.
Instead, it provides a comprehensive set of AI skills, sub-agents, and workflows.

The AI uses the web/browser capabilities available in its environment (such as Antigravity). Live results completely depend on the user's local tools. If no web search or browser is available, the AI will use a safe fallback strategy relying on local knowledge and will mark all data as requiring verification.

## Installation

You can install this Travel Skills Pack directly into another Antigravity project:

```bash
ultimate-travel-agent install-skills --target <path-to-project>
```

To also install the recommended sub-agents and workflows:

```bash
ultimate-travel-agent install-skills --target <path-to-project> --include-agents --include-workflows
```

## How to use

1. **Fill a travel brief** using the template (`examples/trip-brief-template.md`).
2. **Launch the complete workflow** (`.agents/workflows/plan-complete-trip.md`).
3. The orchestrator will mobilize sub-agents to research destinations, build an itinerary, and check the budget.
4. You will receive a fully structured travel folder with links and recommendations.

## Safety and Limits

- **No booking:** The AI will never make purchases or reservations.
- **No personal data:** The AI will never enter payment details or personal information.
- The AI will never bypass paywalls or site restrictions.
- All recommendations must be verified by the user before booking.

## Sources Hierarchy

The agents follow a strict sourcing policy:
- **Tier 1:** Official source
- **Tier 2:** Official operator or direct supplier
- **Tier 3:** Recognized tourist institution
- **Tier 4:** Recognized editorial source
- **Tier 5:** Community reviews
- **Tier 6:** Social media / discovery only

## Example Expected Output

```yaml
summary: "7-day city break in Tokyo focusing on food and culture."
recommendations:
  - name: "Senso-ji Temple"
    type: "culture"
    confidence: "high"
source_log:
  - url: "https://www.japan.travel"
    tier: 1
verification_required:
  - "Verify exact train schedules on the official JR Pass website."
risks:
  - "High crowds expected during golden week."
```

## Archived Prototype

The original experimental MCP/API prototype has been archived and can be found on the branch:
`archive/mcp-api-prototype-v1.2`
