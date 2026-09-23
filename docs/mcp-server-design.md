# MCP server design

## Understanding and constraints

Ultimate Travel Agent remains a skills-first package. The MCP surface is an optional,
local-first adapter over existing deterministic Python functions; it is not a booking
engine, shell gateway, or general filesystem/network proxy. It must preserve the CLI,
the canonical `.agents/` pack, `TravelDossier v1`, and `compact-handoff/v2` on Python
3.10-3.13 across Windows, macOS, and Linux.

The server is intended for one local MCP client over stdio. It does not need daemon,
multi-tenant, or high-throughput infrastructure. Inputs and stable structured outputs
are validated from Pydantic-owned contracts. Filesystem operations are restricted to a
configured root, network destinations remain constrained by the existing connector and
webhook models, and no tool executes user-supplied commands.

## Approaches considered

1. **Thin low-level MCP adapter (selected).** Keep explicit `mcp.types.Tool`
   declarations for static auditing, derive JSON Schemas from Pydantic models, and
   dispatch calls to existing business functions. This preserves annotations that are
   easy to scan while avoiding duplicated validation and business logic.
2. **FastMCP decorators.** Concise for new tools, but would obscure the existing
   catalogue, make static annotation auditing less direct, and require wrapping many
   established model combinations in function signatures.
3. **CLI subprocess adapter.** Maximally reuses CLI entry points, but serializes through
   temporary files, weakens structured error handling, and would create an unnecessary
   command-execution boundary. It is rejected.

## Architecture

- `mcp/schemas.py` owns MCP request envelopes and stable response envelopes. Nested
  domain data reuses existing Pydantic models.
- `mcp_tools.py` remains the public catalogue. Every `Tool` contains an inline
  `ToolAnnotations(...)` with all four explicit booleans. Input and output schemas are
  supplied by the Pydantic contracts.
- `mcp/handlers.py` validates request envelopes, enforces the filesystem root, invokes
  existing Python functions directly, and serializes safe structured results.
- `mcp/server.py` provides MCP initialization, `tools/list`, and validated `tools/call`
  over stdio. SDK validation checks both input and declared output schemas.
- `ultimate-travel-agent-mcp` launches the server. The normal package remains usable
  without the optional `mcp` dependency.

`connector-fetch` remains available for compatibility but is classified as a remote
writer because it permits POST. `connector-read` accepts GET only and is the explicitly
read-only alternative. Neither tool performs purchases or booking actions.

## Errors and security

Expected validation, path, and domain failures become concise MCP errors without
tracebacks, environment values, request headers, response bodies, or credentials.
Filesystem paths are resolved below the configured server root before use. Existing
same-host redirect, HTTPS, response-size, secret-source, and sensitive-field controls
remain authoritative for network tools.

## Testing strategy

Deterministic tests cover static annotations, schema validity, schema/model parity,
read-only connector enforcement, path containment, dispatcher behavior, and a real
stdio MCP initialization/list/call smoke flow. Skill trigger evals use checked-in cases
and deterministic expected/forbidden ownership labels; optional LLM judging is kept
outside the default CI path.

## Decision log

- Selected the low-level SDK server to keep the registry explicit and statically
  auditable.
- Selected Pydantic as the schema source of truth to prevent hand-maintained drift.
- Selected direct Python dispatch and rejected subprocess reuse for safety and typed
  results.
- Selected a compatibility-preserving connector split: keep `connector-fetch`, fix its
  annotation, and add `connector-read`.
- Selected stdio and a bounded local root; HTTP transport and arbitrary external roots
  are explicit non-goals.
- Selected deterministic skill-routing evals for CI; paid LLM evals are optional future
  work.
