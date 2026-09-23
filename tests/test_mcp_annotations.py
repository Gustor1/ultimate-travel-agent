"""Tests for MCP tool annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint).

These tests verify that every tool registered in mcp_tools.py carries all four
safety/behaviour hint annotations as explicit booleans.  No network access or
API keys are required.
"""

from __future__ import annotations

import pytest

from ultimate_travel_agent.mcp_tools import TOOLS, Tool, get_tool, list_tools

# ---------------------------------------------------------------------------
# The canonical set of CLI tool names mirrors cli.py subcommands exactly.
# Update this set whenever a tool is added or removed from the CLI.
# ---------------------------------------------------------------------------
EXPECTED_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "install-skills",
        "uninstall-skills",
        "list-skills",
        "validate-skills",
        "validate-dossier",
        "validate-handoff",
        "prompt-audit",
        "normalize-source-url",
        "profile-save",
        "profile-show",
        "export-dossier",
        "revalidation-plan",
        "price-watch",
        "flight-search-plan",
        "flight-search-coverage",
        "hotel-search-plan",
        "hotel-search-coverage",
        "hotel-compare",
        "hotel-mobility",
        "compare-total-cost",
        "disruption-plan",
        "connector-fetch",
        "connector-read",
        "adaptive-day",
        "route-optimize",
        "group-decide",
        "neighborhood-score",
        "booking-handoff",
        "trip-mode",
        "notify-webhook",
    }
)

_ANNOTATION_FIELDS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


class TestToolRegistry:
    """Structural integrity of the tool registry."""

    def test_tool_names_match_expected_set(self) -> None:
        """Registered tool names exactly match the canonical CLI subcommand set."""
        registered = frozenset(t.name for t in list_tools())
        assert registered == EXPECTED_TOOL_NAMES

    def test_tool_count_matches_cli(self) -> None:
        """Tool count equals the number of CLI subcommands (source of truth)."""
        assert len(list_tools()) == len(EXPECTED_TOOL_NAMES)

    def test_no_duplicate_tool_names(self) -> None:
        """Each tool name appears exactly once."""
        names = [t.name for t in list_tools()]
        assert len(names) == len(set(names))

    def test_list_tools_returns_shallow_copy(self) -> None:
        """list_tools() must not return the same list object each time."""
        first = list_tools()
        second = list_tools()
        assert first is not second
        assert first == second


class TestAnnotationPresence:
    """All four annotations are present and are explicit booleans on every tool."""

    @pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.name)
    def test_tool_has_annotations_object(self, tool: object) -> None:
        assert isinstance(tool, Tool)
        assert tool.annotations is not None, f"{tool.name}: annotations must not be None"  # type: ignore[union-attr]

    @pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.name)
    @pytest.mark.parametrize("field", _ANNOTATION_FIELDS)
    def test_annotation_field_is_explicit_bool(self, tool: object, field: str) -> None:
        assert isinstance(tool, Tool)
        annotations = tool.annotations  # type: ignore[union-attr]
        value = getattr(annotations, field)
        assert value is not None, (
            f"{tool.name}.annotations.{field} must be an explicit bool, got None"  # type: ignore[union-attr]
        )
        assert isinstance(value, bool), (
            f"{tool.name}.annotations.{field} must be bool, got {type(value).__name__}"  # type: ignore[union-attr]
        )


class TestLocalReadonlyTool:
    """validate-dossier is a canonical example of a local, read-only tool."""

    def test_validate_dossier_is_read_only(self) -> None:
        tool = get_tool("validate-dossier")
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is True

    def test_validate_dossier_is_not_destructive(self) -> None:
        tool = get_tool("validate-dossier")
        assert tool.annotations is not None
        assert tool.annotations.destructiveHint is False

    def test_validate_dossier_is_idempotent(self) -> None:
        tool = get_tool("validate-dossier")
        assert tool.annotations is not None
        assert tool.annotations.idempotentHint is True

    def test_validate_dossier_is_not_open_world(self) -> None:
        tool = get_tool("validate-dossier")
        assert tool.annotations is not None
        assert tool.annotations.openWorldHint is False


class TestNetworkTool:
    """connector-fetch is the canonical example of a network-accessing tool."""

    def test_connector_fetch_is_open_world(self) -> None:
        tool = get_tool("connector-fetch")
        assert tool.annotations is not None
        assert tool.annotations.openWorldHint is True

    def test_connector_fetch_is_not_read_only(self) -> None:
        """The compatibility connector permits POST and may mutate remote state."""
        tool = get_tool("connector-fetch")
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is False

    def test_connector_fetch_is_not_destructive(self) -> None:
        tool = get_tool("connector-fetch")
        assert tool.annotations is not None
        assert tool.annotations.destructiveHint is False

    def test_connector_fetch_is_not_idempotent(self) -> None:
        """POST requests are possible; repeated calls are not guaranteed idempotent."""
        tool = get_tool("connector-fetch")
        assert tool.annotations is not None
        assert tool.annotations.idempotentHint is False

    def test_connector_read_is_read_only_and_idempotent(self) -> None:
        tool = get_tool("connector-read")
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.destructiveHint is False
        assert tool.annotations.idempotentHint is True
        assert tool.annotations.openWorldHint is True


class TestWebhookTool:
    """notify-webhook sends HTTP POSTs and is therefore open-world and non-idempotent."""

    def test_notify_webhook_is_open_world(self) -> None:
        tool = get_tool("notify-webhook")
        assert tool.annotations is not None
        assert tool.annotations.openWorldHint is True

    def test_notify_webhook_is_not_idempotent(self) -> None:
        """Each call triggers a new delivery."""
        tool = get_tool("notify-webhook")
        assert tool.annotations is not None
        assert tool.annotations.idempotentHint is False

    def test_notify_webhook_is_not_read_only(self) -> None:
        """Webhook POSTs write to a remote endpoint."""
        tool = get_tool("notify-webhook")
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is False


class TestExportDossier:
    """export-dossier writes a local file — special-cased in the requirements."""

    def test_export_dossier_is_not_read_only(self) -> None:
        """Writing a file makes this tool non-read-only."""
        tool = get_tool("export-dossier")
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is False

    def test_export_dossier_is_not_destructive(self) -> None:
        """The tool writes to a user-specified output path; no pre-existing data is deleted."""
        tool = get_tool("export-dossier")
        assert tool.annotations is not None
        assert tool.annotations.destructiveHint is False

    def test_export_dossier_is_idempotent(self) -> None:
        """Identical inputs produce identical output bytes each time."""
        tool = get_tool("export-dossier")
        assert tool.annotations is not None
        assert tool.annotations.idempotentHint is True

    def test_export_dossier_is_not_open_world(self) -> None:
        """Export functions transform a supplied dossier; no network calls are made."""
        tool = get_tool("export-dossier")
        assert tool.annotations is not None
        assert tool.annotations.openWorldHint is False


class TestDestructiveTool:
    """uninstall-skills deletes local files and is the only destructive tool."""

    def test_uninstall_skills_is_destructive(self) -> None:
        tool = get_tool("uninstall-skills")
        assert tool.annotations is not None
        assert tool.annotations.destructiveHint is True

    def test_uninstall_skills_is_not_open_world(self) -> None:
        tool = get_tool("uninstall-skills")
        assert tool.annotations is not None
        assert tool.annotations.openWorldHint is False

    def test_no_other_tool_is_destructive(self) -> None:
        """Only uninstall-skills should be marked destructive."""
        destructive = [
            t.name
            for t in list_tools()
            if t.annotations is not None and t.annotations.destructiveHint is True
        ]
        assert destructive == ["uninstall-skills"]


class TestOpenWorldTools:
    """Network tools carry openWorldHint=True; local tools carry openWorldHint=False."""

    def test_only_network_tools_are_open_world(self) -> None:
        """connector-fetch and notify-webhook are the only open-world tools."""
        open_world = frozenset(
            t.name
            for t in list_tools()
            if t.annotations is not None and t.annotations.openWorldHint is True
        )
        assert open_world == {"connector-fetch", "connector-read", "notify-webhook"}

    def test_all_other_tools_are_closed_world(self) -> None:
        closed_world = [
            t.name
            for t in list_tools()
            if t.annotations is not None and t.annotations.openWorldHint is False
        ]
        assert len(closed_world) == len(list_tools()) - 3
