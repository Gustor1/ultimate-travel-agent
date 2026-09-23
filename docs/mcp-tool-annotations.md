# MCP Tool Safety Annotations

Every tool exposed by `ultimate-travel-agent` carries four explicit behaviour
hints in the `annotations` field of the MCP `Tool` object.  These hints
help MCP clients (agents, orchestrators, registries) reason about what a tool
does before calling it.

> **Important**: These hints describe *expected* behaviour and are advisory.
> They do **not** replace the server-side access controls, input validation,
> and sandboxing that the host runtime must enforce.

---

## The Four Hints

| Hint | Type | Meaning |
|---|---|---|
| `readOnlyHint` | `bool` | `true` when the tool neither modifies local files nor mutates remote state. |
| `destructiveHint` | `bool` | `true` when the tool can delete or irreversibly overwrite existing data. Implies `readOnlyHint: false`. |
| `idempotentHint` | `bool` | `true` when calling the tool multiple times with identical inputs produces the same observable result as calling it once. |
| `openWorldHint` | `bool` | `true` when the tool contacts the network, an external API, or any dynamic data source outside the local process. |

All four fields are **always explicit booleans** in this pack — none is ever
left as `null` (the SDK default). This is required by the M8ven registry audit.

---

## Tool Classification

### Local read-only / pure computation

Most tools in this pack are deterministic transformations of supplied input
data.  They do not write files, delete data, or open network connections.

```
readOnlyHint: true   destructiveHint: false   idempotentHint: true   openWorldHint: false
```

Examples: `validate-dossier`, `validate-handoff`, `flight-search-coverage`,
`compare-total-cost`, `disruption-plan`, `adaptive-day`, `route-optimize`.

### Local file writers

These tools create or overwrite a file on the local filesystem.

```
readOnlyHint: false   destructiveHint: false   idempotentHint: true   openWorldHint: false
```

Examples: `install-skills`, `profile-save`, `export-dossier`,
`flight-search-plan`, `hotel-search-plan`.

**Special case — `export-dossier`**: writes an output artifact in a format
chosen by the caller (ics, geojson, pdf, checklist, offline, html).  It is
idempotent because identical inputs produce byte-identical output; it is not
open-world because the export functions do not make network calls.

### Destructive tool

`uninstall-skills` deletes installed files and is the only tool marked
`destructiveHint: true`.  It remains idempotent (a no-op if files are absent)
and is not open-world.

```
readOnlyHint: false   destructiveHint: true   idempotentHint: true   openWorldHint: false
```

### Network-accessing tools

Only two tools contact external endpoints:

| Tool | Reason | idempotent |
|---|---|---|
| `connector-fetch` | Executes a bounded live HTTPS JSON request | `false` (POST possible) |
| `notify-webhook` | Sends a signed HTTPS POST notification | `false` (each call delivers) |

```
openWorldHint: true
```

### Time-sensitive local tools

`booking-handoff` and `trip-mode` read local state but their output depends
on the current time, so repeated calls may return different results.

```
readOnlyHint: true   destructiveHint: false   idempotentHint: false   openWorldHint: false
```

---

## Implementation

Annotations are declared in
[`src/ultimate_travel_agent/mcp_tools.py`](../src/ultimate_travel_agent/mcp_tools.py)
using `mcp.types.ToolAnnotations`.  The registry is a **pure data module** —
it does not start a server or make network connections on import.

```python
from ultimate_travel_agent.mcp_tools import list_tools, get_tool

tools = list_tools()          # list[mcp.types.Tool]
t = get_tool("validate-dossier")
print(t.annotations.readOnlyHint)   # True
```

Tests in
[`tests/test_mcp_annotations.py`](../tests/test_mcp_annotations.py)
assert that all tools carry explicit boolean values for all four fields.
