"""MCP tool registry for ultimate-travel-agent.

Declares all 30 CLI tools as `mcp.types.Tool` objects with explicit
`ToolAnnotations` so that MCP clients and registries (e.g. M8ven) can
discover their safety/behaviour hints.

This module is a **pure data declaration** -- it does not start a server,
open network connections, or read files.  Import it wherever you need the
tool list::

    from ultimate_travel_agent.mcp_tools import list_tools, TOOLS

The `mcp` package is an optional dependency.  If it is not installed, an
`ImportError` is raised with an actionable message.

.. note::
    These hints describe expected behaviour for MCP *clients*.  They do **not**
    replace the server-side access controls, input validation, and sandboxing
    that the host runtime is responsible for enforcing.
"""

from __future__ import annotations

from typing import Any

try:
    from mcp.types import Tool, ToolAnnotations
except ImportError:  # pragma: no cover
    from pydantic import BaseModel, ConfigDict

    class ToolAnnotations(BaseModel):  # type: ignore[no-redef]
        title: str | None = None
        readOnlyHint: bool | None = None
        destructiveHint: bool | None = None
        idempotentHint: bool | None = None
        openWorldHint: bool | None = None

        model_config = ConfigDict(extra="allow")

    class Tool(BaseModel):  # type: ignore[no-redef]
        name: str
        description: str | None = None
        inputSchema: dict[str, Any]
        outputSchema: dict[str, Any] | None = None
        annotations: ToolAnnotations | None = None

        model_config = ConfigDict(extra="allow")


# ---------------------------------------------------------------------------
# Minimal reusable input schema (each tool takes a single JSON object).
# Individual tools declare their own structured inputs at invocation time;
# the schema here is intentionally permissive so that this registry module
# has no coupling to the internal Pydantic models.
# ---------------------------------------------------------------------------
_OBJECT_INPUT: dict[str, object] = {"type": "object"}

# ---------------------------------------------------------------------------
# Annotation factory helpers
# ---------------------------------------------------------------------------


def _local_readonly() -> ToolAnnotations:
    """Pure local read / calculation; no I/O side effects."""
    return ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )


def _local_writer(*, destructive: bool = False, idempotent: bool = True) -> ToolAnnotations:
    """Writes or deletes local files; no network access."""
    return ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=destructive,
        idempotentHint=idempotent,
        openWorldHint=False,
    )


def _network_readonly(*, idempotent: bool = True) -> ToolAnnotations:
    """Contacts an external network endpoint; does not modify remote state."""
    return ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=idempotent,
        openWorldHint=True,
    )


def _network_writer(*, idempotent: bool = False) -> ToolAnnotations:
    """Sends data to an external network endpoint (e.g. webhook POST)."""
    return ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=idempotent,
        openWorldHint=True,
    )


# ---------------------------------------------------------------------------
# Tool catalogue -- 30 tools matching the CLI subcommands in cli.py
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # ------------------------------------------------------------------
    # Skills management (local file I/O)
    # ------------------------------------------------------------------
    Tool(
        name="install-skills",
        description=(
            "Install Ultimate Travel Agent skills, agents, and workflows into a target "
            "project directory. Skips existing files unless --force is set."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_writer(destructive=False, idempotent=True),
    ),
    Tool(
        name="uninstall-skills",
        description=(
            "Remove previously installed travel skills, agents, and workflows from a "
            "target project directory."
        ),
        inputSchema=_OBJECT_INPUT,
        # Deletes files -> destructiveHint=True; noop if already absent -> idempotent=True
        annotations=_local_writer(destructive=True, idempotent=True),
    ),
    Tool(
        name="list-skills",
        description="List all available travel skills in the installed pack.",
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="validate-skills",
        description=(
            "Validate the quality, schema, and safety invariants of all skills "
            "in the installed pack."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Contract validators (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="validate-dossier",
        description=(
            "Validate a JSON or YAML file against the TravelDossier v1 contract, "
            "checking evidence freshness, source authority, and readiness gates."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="validate-handoff",
        description=(
            "Validate a JSON or YAML file against the compact-handoff/v2 contract, "
            "checking stage, status, coverage, and blockers."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Corpus & URL utilities (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="prompt-audit",
        description=(
            "Measure the canonical prompt corpus character count and a stable token "
            "proxy for regression tracking. Does not call any provider billing API."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="normalize-source-url",
        description=(
            "Canonicalize an HTTP(S) source URL for deduplication by stripping "
            "tracking parameters while preserving content-identifying ones."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Traveler profile (local file I/O)
    # ------------------------------------------------------------------
    Tool(
        name="profile-save",
        description=(
            "Validate and atomically persist a privacy-minimal traveler profile "
            "as a normalized JSON file."
        ),
        inputSchema=_OBJECT_INPUT,
        # Writes one file; identical inputs produce identical output -> idempotent
        annotations=_local_writer(destructive=False, idempotent=True),
    ),
    Tool(
        name="profile-show",
        description="Load and display a validated traveler profile as normalized JSON.",
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Dossier export (local file I/O, no network)
    # ------------------------------------------------------------------
    Tool(
        name="export-dossier",
        description=(
            "Validate a dossier and export it to a portable artifact in one of the "
            "supported formats: ics, geojson, pdf, checklist, offline, html. "
            "Writes the output to a user-specified path."
        ),
        inputSchema=_OBJECT_INPUT,
        # Writes a file (readOnly=False); no data deletion (destructive=False);
        # same inputs produce byte-identical output (idempotent=True);
        # export functions make no network calls (openWorld=False).
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    # ------------------------------------------------------------------
    # Monitoring (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="revalidation-plan",
        description=(
            "Generate a pre-departure revalidation schedule from a validated dossier, "
            "calculating task deadlines relative to the departure date."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="price-watch",
        description=(
            "Assess a sourced flight or hotel price-history series and optionally "
            "schedule a price-alert policy against current state."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Flight search (local computation -- generates a search plan to file)
    # ------------------------------------------------------------------
    Tool(
        name="flight-search-plan",
        description=(
            "Generate an exhaustive four-pass flexible-flight search matrix from a "
            "FlightSearchRequest and write the plan to a JSON output file."
        ),
        inputSchema=_OBJECT_INPUT,
        # Writes an output JSON file; no network call made by this tool
        annotations=_local_writer(destructive=False, idempotent=True),
    ),
    Tool(
        name="flight-search-coverage",
        description=(
            "Verify that every cell in a flight-search plan was attempted and "
            "optionally require booking-level source evidence."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Hotel search (local computation -- generates a research plan to file)
    # ------------------------------------------------------------------
    Tool(
        name="hotel-search-plan",
        description=(
            "Generate transit-first hotel comparison tasks from a HotelSearchRequest "
            "and write the research plan to a JSON output file."
        ),
        inputSchema=_OBJECT_INPUT,
        # Writes an output JSON file; no network call made by this tool
        annotations=_local_writer(destructive=False, idempotent=True),
    ),
    Tool(
        name="hotel-search-coverage",
        description=(
            "Verify hotel research source coverage and direct-check completion "
            "from a HotelResearchPlan."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="hotel-compare",
        description=(
            "Compare normalized room quotes and transit access scores for one hotel property."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="hotel-mobility",
        description=(
            "Score door-to-door transit quality from a hotel to important trip "
            "anchors using sourced journey data."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Cost & disruption (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="compare-total-cost",
        description=(
            "Compare complete travel options including monetary cost, time value, "
            "and transfer-risk exposure."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="disruption-plan",
        description=(
            "Build a recovery plan that replaces only the disrupted itinerary items "
            "while preserving unaffected ones. Supports cascading missed-connection "
            "propagation."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Live connector (network I/O -- the only tool that opens HTTP connections)
    # ------------------------------------------------------------------
    Tool(
        name="connector-fetch",
        description=(
            "Execute one bounded live JSON connector request against a pre-configured "
            "HTTPS endpoint. Credentials are supplied via environment variables and "
            "never included in the result. Supports optional response normalization."
        ),
        inputSchema=_OBJECT_INPUT,
        # Contacts an external API; POST is possible -> non-idempotent
        annotations=_network_readonly(idempotent=False),
    ),
    # ------------------------------------------------------------------
    # Day planning (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="adaptive-day",
        description=(
            "Build essential, balanced, rain, and low-energy day variants from a "
            "list of activity candidates."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    Tool(
        name="route-optimize",
        description=(
            "Optimize a day's visit order using sourced travel times and venue opening windows."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Group decision (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="group-decide",
        description=(
            "Rank complete group travel options by aggregating participant ballots "
            "and applying hard vetoes."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Neighborhood (pure computation)
    # ------------------------------------------------------------------
    Tool(
        name="neighborhood-score",
        description=(
            "Score evidence-backed neighborhood quality against traveler requirements "
            "such as transit access, safety, and walkability."
        ),
        inputSchema=_OBJECT_INPUT,
        annotations=_local_readonly(),
    ),
    # ------------------------------------------------------------------
    # Booking handoff (local state check; time-sensitive)
    # ------------------------------------------------------------------
    Tool(
        name="booking-handoff",
        description=(
            "Prepare or confirm a user-controlled booking checkout handoff, "
            "checking price-lock deadlines and generating a direct operator link."
        ),
        inputSchema=_OBJECT_INPUT,
        # Time-sensitive deadline checking makes repeated calls non-idempotent
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    ),
    # ------------------------------------------------------------------
    # Trip companion (local state; time-sensitive)
    # ------------------------------------------------------------------
    Tool(
        name="trip-mode",
        description=(
            "Show the current itinerary item, next required action, and offline "
            "readiness status relative to the current time."
        ),
        inputSchema=_OBJECT_INPUT,
        # Current-time dependency makes repeated calls non-idempotent
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    ),
    # ------------------------------------------------------------------
    # Webhook notification (network I/O -- HTTP POST)
    # ------------------------------------------------------------------
    Tool(
        name="notify-webhook",
        description=(
            "Deliver one explicitly configured signed HTTPS webhook notification. "
            "The signing secret is supplied via an environment variable. "
            "No notification content is included in the receipt."
        ),
        inputSchema=_OBJECT_INPUT,
        # Sends an HTTP POST; each call triggers a new delivery -> non-idempotent
        annotations=_network_writer(idempotent=False),
    ),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_TOOL_INDEX: dict[str, Tool] = {tool.name: tool for tool in TOOLS}


def list_tools() -> list[Tool]:
    """Return the complete list of MCP tool definitions with safety annotations.

    The returned list is a shallow copy; callers must not mutate the elements.
    """
    return list(TOOLS)


def get_tool(name: str) -> Tool:
    """Return a single tool definition by its CLI name.

    Raises `KeyError` if *name* is not registered.
    """
    return _TOOL_INDEX[name]


__all__ = ["TOOLS", "Tool", "ToolAnnotations", "get_tool", "list_tools"]
