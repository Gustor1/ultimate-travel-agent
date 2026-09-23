"""Statically auditable MCP tool catalogue.

The catalogue is importable without starting a server. Safety annotations are
intentionally repeated as inline boolean literals so static registries do not need to
execute helper functions to understand tool behaviour.
"""

from __future__ import annotations

from typing import Any

from ultimate_travel_agent.mcp.schemas import get_input_model, get_output_model

try:
    from mcp.types import Tool, ToolAnnotations
except ImportError:  # pragma: no cover - normal package does not require the MCP extra
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


def _input(name: str) -> dict[str, Any]:
    return get_input_model(name).model_json_schema()


def _output(name: str) -> dict[str, Any]:
    return get_output_model(name).model_json_schema()


TOOLS: list[Tool] = [
    Tool(
        name="install-skills",
        description="Install the canonical skills pack below the configured MCP root.",
        inputSchema=_input("install-skills"),
        outputSchema=_output("install-skills"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="uninstall-skills",
        description="Remove manifest-tracked installed files below the configured MCP root.",
        inputSchema=_input("uninstall-skills"),
        outputSchema=_output("uninstall-skills"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="list-skills",
        description="List skills in the canonical bundled pack.",
        inputSchema=_input("list-skills"),
        outputSchema=_output("list-skills"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="validate-skills",
        description="Validate skill quality and safety invariants.",
        inputSchema=_input("validate-skills"),
        outputSchema=_output("validate-skills"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="validate-dossier",
        description="Validate a TravelDossier v1 object and return normalized data when valid.",
        inputSchema=_input("validate-dossier"),
        outputSchema=_output("validate-dossier"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="validate-handoff",
        description="Validate a compact-handoff/v2 object.",
        inputSchema=_input("validate-handoff"),
        outputSchema=_output("validate-handoff"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="prompt-audit",
        description="Measure the prompt corpus with a deterministic character/token proxy.",
        inputSchema=_input("prompt-audit"),
        outputSchema=_output("prompt-audit"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="normalize-source-url",
        description="Canonicalize a safe HTTP(S) evidence URL for deduplication.",
        inputSchema=_input("normalize-source-url"),
        outputSchema=_output("normalize-source-url"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="profile-save",
        description="Atomically save a privacy-minimal profile below the MCP root.",
        inputSchema=_input("profile-save"),
        outputSchema=_output("profile-save"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="profile-show",
        description="Load a validated traveler profile below the MCP root.",
        inputSchema=_input("profile-show"),
        outputSchema=_output("profile-show"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="export-dossier",
        description="Write a validated dossier export below the MCP root.",
        inputSchema=_input("export-dossier"),
        outputSchema=_output("export-dossier"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="revalidation-plan",
        description="Build a deterministic pre-departure revalidation schedule.",
        inputSchema=_input("revalidation-plan"),
        outputSchema=_output("revalidation-plan"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="price-watch",
        description="Assess timestamped price observations or schedule a local alert decision.",
        inputSchema=_input("price-watch"),
        outputSchema=_output("price-watch"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="flight-search-plan",
        description="Generate a four-pass flight matrix and optionally save it below the MCP root.",
        inputSchema=_input("flight-search-plan"),
        outputSchema=_output("flight-search-plan"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="flight-search-coverage",
        description="Assess completion and booking evidence across a flight-search plan.",
        inputSchema=_input("flight-search-coverage"),
        outputSchema=_output("flight-search-coverage"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="hotel-search-plan",
        description="Generate hotel research tasks and optionally save them below the MCP root.",
        inputSchema=_input("hotel-search-plan"),
        outputSchema=_output("hotel-search-plan"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="hotel-search-coverage",
        description="Assess hotel discovery, transit, and official verification coverage.",
        inputSchema=_input("hotel-search-coverage"),
        outputSchema=_output("hotel-search-coverage"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="hotel-compare",
        description="Compare matched room quotes and transit evidence for one property.",
        inputSchema=_input("hotel-compare"),
        outputSchema=_output("hotel-compare"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="hotel-mobility",
        description="Score sourced door-to-door journeys from a hotel to trip anchors.",
        inputSchema=_input("hotel-mobility"),
        outputSchema=_output("hotel-mobility"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="compare-total-cost",
        description="Compare exact door-to-door costs, time value, and risk reserve.",
        inputSchema=_input("compare-total-cost"),
        outputSchema=_output("compare-total-cost"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="disruption-plan",
        description="Build a deterministic recovery plan for disrupted itinerary items.",
        inputSchema=_input("disruption-plan"),
        outputSchema=_output("disruption-plan"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="connector-fetch",
        description=(
            "Compatibility connector for bounded HTTPS GET or POST JSON requests. "
            "Use connector-read when remote mutation must be impossible."
        ),
        inputSchema=_input("connector-fetch"),
        outputSchema=_output("connector-fetch"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    ),
    Tool(
        name="connector-read",
        description="Execute one bounded HTTPS GET JSON request; POST is rejected by schema.",
        inputSchema=_input("connector-read"),
        outputSchema=_output("connector-read"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    ),
    Tool(
        name="adaptive-day",
        description="Build essential, balanced, rain, and low-energy day variants.",
        inputSchema=_input("adaptive-day"),
        outputSchema=_output("adaptive-day"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="route-optimize",
        description="Optimize visit order from sourced travel times and opening windows.",
        inputSchema=_input("route-optimize"),
        outputSchema=_output("route-optimize"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="group-decide",
        description="Rank complete group ballots while enforcing hard vetoes.",
        inputSchema=_input("group-decide"),
        outputSchema=_output("group-decide"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="neighborhood-score",
        description="Score a neighborhood from dated evidence and traveler thresholds.",
        inputSchema=_input("neighborhood-score"),
        outputSchema=_output("neighborhood-score"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="booking-handoff",
        description="Prepare or confirm a user-controlled checkout handoff without purchasing.",
        inputSchema=_input("booking-handoff"),
        outputSchema=_output("booking-handoff"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="trip-mode",
        description="Compute the current trip state from an explicit timestamp.",
        inputSchema=_input("trip-mode"),
        outputSchema=_output("trip-mode"),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    ),
    Tool(
        name="notify-webhook",
        description="Send one explicitly configured signed HTTPS webhook notification.",
        inputSchema=_input("notify-webhook"),
        outputSchema=_output("notify-webhook"),
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    ),
]

_TOOL_INDEX: dict[str, Tool] = {tool.name: tool for tool in TOOLS}


def list_tools() -> list[Tool]:
    return list(TOOLS)


def get_tool(name: str) -> Tool:
    return _TOOL_INDEX[name]


__all__ = ["TOOLS", "Tool", "ToolAnnotations", "get_tool", "list_tools"]
