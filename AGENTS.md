# Agent routing

For a travel request, start with `.agents/skills/travel-orchestrator/SKILL.md`. Load only the specialist skills and shared references that it selects; never preload the whole pack. Treat `docs/`, `examples/`, `src/`, and `tests/` as development material unless the user asks about the repository or a skill explicitly calls a deterministic CLI command. Persist evidence in artifacts and exchange `compact-handoff/v2` IDs instead of repeating research payloads.

For repository development, preserve `.agents/` as the single canonical pack and run the focused tests for every changed contract or tool.
