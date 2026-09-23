# MCP tools, schemas, and safety annotations

The optional stdio server exposes 30 tools. Every declaration in
`src/ultimate_travel_agent/mcp_tools.py` contains all four MCP safety hints as inline
boolean literals so static analysers do not need to resolve helper functions.

The hints are advisory metadata, not an authorization boundary:

- `readOnlyHint`: no local or remote mutation is possible;
- `destructiveHint`: tracked data may be deleted or irreversibly replaced;
- `idempotentHint`: repeating identical explicit inputs has the same observable effect;
- `openWorldHint`: the call contacts an external endpoint.

## Catalogue

| Tools | Read-only | Destructive | Idempotent | Open world |
|---|---:|---:|---:|---:|
| `list-skills`, `validate-skills`, `validate-dossier`, `validate-handoff`, `prompt-audit`, `normalize-source-url`, `profile-show`, `revalidation-plan`, `price-watch`, `flight-search-coverage`, `hotel-search-coverage`, `hotel-compare`, `hotel-mobility`, `compare-total-cost`, `disruption-plan`, `adaptive-day`, `route-optimize`, `group-decide`, `neighborhood-score`, `booking-handoff`, `trip-mode` | true | false | true | false |
| `install-skills`, `profile-save`, `export-dossier`, `flight-search-plan`, `hotel-search-plan` | false | false | true | false |
| `uninstall-skills` | false | true | true | false |
| `connector-read` | true | false | true | true |
| `connector-fetch` | false | false | false | true |
| `notify-webhook` | false | false | false | true |

`booking-handoff` and `trip-mode` take an explicit timestamp. They are deterministic
and idempotent for identical complete inputs; neither performs checkout or network I/O.

`connector-fetch` remains for compatibility and accepts GET or POST, so it cannot be
declared read-only. New integrations that only retrieve JSON should use
`connector-read`, whose request contract accepts GET only.

## Schemas

All 30 tools have non-generic `inputSchema` and `outputSchema` values generated from
Pydantic models in `mcp/schemas.py`. Request envelope models forbid unknown top-level
fields. Nested business contracts reuse the existing domain models, including their
enums, numeric limits, formats, regexes, required fields, and cross-field validators.

The low-level MCP SDK validates inputs before dispatch and validates structured outputs
against the advertised output schema. Tests additionally compare every catalogue schema
with the current model-generated schema and run JSON Schema meta-validation.

## Server and containment

Install and start the optional server with:

```bash
python -m pip install "ultimate-travel-agent[mcp]"
ultimate-travel-agent-mcp
```

The server uses stdio only. Filesystem operations resolve below
`ULTIMATE_TRAVEL_AGENT_MCP_ROOT`, defaulting to the current working directory. The
dispatcher invokes Python functions directly; it never executes a user-supplied shell
command. Network tools retain HTTPS, destination, redirect, size, credential, and
sensitive-field validation.
