from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

import jsonschema
import pytest

from ultimate_travel_agent.mcp_tools import list_tools

ROOT = Path(__file__).resolve().parents[1]


def test_annotations_are_inline_static_boolean_literals() -> None:
    source_path = ROOT / "src" / "ultimate_travel_agent" / "mcp_tools.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    tool_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Tool"
    ]
    assert len(tool_calls) == 30
    expected = {
        "readOnlyHint",
        "destructiveHint",
        "idempotentHint",
        "openWorldHint",
    }
    for call in tool_calls:
        name_keyword = next(keyword for keyword in call.keywords if keyword.arg == "name")
        assert isinstance(name_keyword.value, ast.Constant)
        tool_name = name_keyword.value.value
        annotations = next(
            keyword.value for keyword in call.keywords if keyword.arg == "annotations"
        )
        assert isinstance(annotations, ast.Call), tool_name
        assert isinstance(annotations.func, ast.Name), tool_name
        assert annotations.func.id == "ToolAnnotations", tool_name
        values = {keyword.arg: keyword.value for keyword in annotations.keywords}
        assert set(values) == expected, tool_name
        assert all(
            isinstance(value, ast.Constant) and isinstance(value.value, bool)
            for value in values.values()
        ), tool_name


@pytest.mark.parametrize("tool", list_tools(), ids=lambda tool: tool.name)
def test_every_tool_has_real_valid_input_and_output_schemas(tool: object) -> None:
    assert hasattr(tool, "inputSchema")
    assert tool.inputSchema != {"type": "object"}  # type: ignore[attr-defined]
    assert tool.inputSchema.get("additionalProperties") is False  # type: ignore[attr-defined]
    jsonschema.Draft202012Validator.check_schema(tool.inputSchema)  # type: ignore[attr-defined]
    assert tool.outputSchema is not None  # type: ignore[attr-defined]
    jsonschema.Draft202012Validator.check_schema(tool.outputSchema)  # type: ignore[attr-defined]


def test_registry_schemas_are_generated_from_declared_models() -> None:
    from ultimate_travel_agent.mcp.schemas import get_input_model, get_output_model

    for tool in list_tools():
        assert tool.inputSchema == get_input_model(tool.name).model_json_schema()
        assert tool.outputSchema == get_output_model(tool.name).model_json_schema()


def test_connector_read_rejects_post_before_network_access() -> None:
    from pydantic import ValidationError

    from ultimate_travel_agent.mcp.schemas import ConnectorReadInput

    payload = {
        "config": {
            "connector_id": "demo",
            "provider": "Demo",
            "domain": "weather",
            "base_url": "https://api.example.com/v1/",
            "allowed_path_prefix": "/v1/",
        },
        "request": {
            "request_id": "request-1",
            "path": "/v1/search",
            "method": "POST",
            "json_body": {"query": "Paris"},
        },
    }
    with pytest.raises(ValidationError, match="GET"):
        ConnectorReadInput.model_validate(payload)


def test_mcp_root_rejects_path_escape(tmp_path: Path) -> None:
    from ultimate_travel_agent.mcp.handlers import ToolDispatcher

    dispatcher = ToolDispatcher(root=tmp_path)
    with pytest.raises(ValueError, match="outside the configured MCP root"):
        dispatcher.resolve_path("../outside.json")


def test_dispatcher_returns_structured_output_for_pure_tool(tmp_path: Path) -> None:
    from ultimate_travel_agent.mcp.handlers import ToolDispatcher

    dispatcher = ToolDispatcher(root=tmp_path)
    result = dispatcher.call(
        "normalize-source-url",
        {"url": "https://example.com/path?utm_source=test&b=2&a=1"},
    )
    assert result == {"url": "https://example.com/path?a=1&b=2"}
    json.dumps(result)


def test_stdio_server_initializes_lists_and_calls_tools(tmp_path: Path) -> None:
    import anyio
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def exercise() -> None:
        environment = dict(os.environ)
        environment["ULTIMATE_TRAVEL_AGENT_MCP_ROOT"] = str(tmp_path)
        environment["PYTHONPATH"] = str(ROOT / "src")
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "ultimate_travel_agent.mcp.server"],
            env=environment,
            cwd=ROOT,
        )
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "ultimate-travel-agent"
                listed = await session.list_tools()
                assert len(listed.tools) == 30
                result = await session.call_tool(
                    "normalize-source-url",
                    {"url": "https://example.com/a?utm_source=x&b=2&a=1"},
                )
                assert result.isError is False
                assert result.structuredContent == {
                    "url": "https://example.com/a?a=1&b=2"
                }
                rejected = await session.call_tool(
                    "connector-read",
                    {
                        "config": {
                            "connector_id": "demo",
                            "provider": "Demo",
                            "domain": "weather",
                            "base_url": "https://api.example.com/v1/",
                            "allowed_path_prefix": "/v1/",
                        },
                        "request": {
                            "request_id": "request-1",
                            "path": "/v1/search",
                            "headers": {"X-Secret-Key": "do-not-leak-this"},
                        },
                    },
                )
                assert rejected.isError is True
                serialized = " ".join(
                    block.text for block in rejected.content if hasattr(block, "text")
                )
                assert "do-not-leak-this" not in serialized

    anyio.run(exercise)
