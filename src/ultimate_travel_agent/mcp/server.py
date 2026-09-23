"""Executable stdio MCP server for Ultimate Travel Agent."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool
from pydantic import ValidationError

from ultimate_travel_agent.mcp.handlers import ToolDispatcher
from ultimate_travel_agent.mcp_tools import list_tools

ROOT_ENVIRONMENT_VARIABLE = "ULTIMATE_TRAVEL_AGENT_MCP_ROOT"


def create_server(root: Path | None = None) -> Server:
    active_root = (
        root
        or Path(os.environ.get(ROOT_ENVIRONMENT_VARIABLE, os.getcwd()))
    ).resolve()
    dispatcher = ToolDispatcher(active_root)
    server = Server(
        "ultimate-travel-agent",
        version="1.9.0",
        instructions=(
            "Local-first travel planning tools. Network and filesystem effects are "
            "declared per tool; no tool performs purchases or arbitrary command execution."
        ),
    )

    @server.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
    async def handle_list_tools() -> list[Tool]:
        return list_tools()

    @server.call_tool(validate_input=True)  # type: ignore[untyped-decorator]
    async def handle_call_tool(
        name: str, arguments: dict[str, Any]
    ) -> dict[str, Any] | CallToolResult:
        try:
            return dispatcher.call(name, arguments)
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
                for error in exc.errors(include_input=False, include_url=False)
            )
            return CallToolResult(
                content=[TextContent(type="text", text=f"Input validation failed: {details}")],
                isError=True,
            )
        except (KeyError, ValueError) as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Tool call failed: {exc}")],
                isError=True,
            )
        except OSError:
            return CallToolResult(
                content=[TextContent(type="text", text="Tool I/O failed")],
                isError=True,
            )
        except Exception:  # pragma: no cover - last-resort secret-safe boundary
            return CallToolResult(
                content=[TextContent(type="text", text="Tool call failed unexpectedly")],
                isError=True,
            )

    return server


async def run_server() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    anyio.run(run_server)


if __name__ == "__main__":
    main()


__all__ = ["ROOT_ENVIRONMENT_VARIABLE", "create_server", "main", "run_server"]
