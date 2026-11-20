---
name: trip-intake
description: Use first when a trip request lacks the origin, dates, budget, pace, or interests needed to plan, or when the user is still choosing where or when to go; produces a privacy-minimal brief and depth mode. Not for researching facts.
---

# Trip Intake

Read `../../shared/planning-depth.md`, `../../shared/compact-research-protocol.md`, and `../../shared/scenario-routing.md`.

## Inputs and tools

Use the user's message, any saved traveler profile (`profile-show` when installed), and earlier answers in the conversation. No live research tools are needed; this skill asks and records.

## Method

1. Extract what is already known. Never re-ask a stated fact.
2. Ask at most one short message of questions, only for facts that change the plan, with a proposed default for each so the user can answer "ok":
   - departure city or region, and whether rail or road is acceptable;
   - dates or season, trip length, and how flexible they are;
   - party (adults, children's ages), and any mobility or dietary need the user volunteers;
   - budget level or ceiling, and what it includes;
   - pace (relaxed, balanced, packed) and top interests or must-sees;
   - lodging style, and anything already booked.
3. Ask nationality or document type only as a category ("passeport UE", "carte d'identité") when the trip crosses a border. Never ask for document numbers, health details, or payment data.
4. Propose the depth mode from `planning-depth.md` and name any triggered scenarios. Record reversible assumptions explicitly instead of asking twice.
5. When the user is undecided about the destination or dates, offer two or three contrasted options with the trade-off in one line each, then stop for their choice.

## Fallback

If the user does not answer, proceed with the stated defaults, mark each as an assumption, and keep date-, budget-, and document-dependent claims unverified until confirmed.

## Outputs

A brief with known facts, assumptions, open questions, depth mode, and active scenario IDs, written in the user's language. In `exhaustive` mode, store it as the run brief and return `compact-handoff/v2`; otherwise hand it directly to `travel-orchestrator`.
