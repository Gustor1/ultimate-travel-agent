"""Entry point for running the web interface directly via python -m ultimate_travel_agent.web."""

import argparse
import sys
import uvicorn


def main() -> None:
    """Launch the local web server."""
    parser = argparse.ArgumentParser(
        prog="ultimate-travel-agent-web",
        description="Local web interface for Ultimate Travel Agent.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host binding (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port binding (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()
    print(f"🌍 Ultimate Travel Agent Web Interface starting at http://{args.host}:{args.port}")
    print("🔒 Running in 100% offline-local mode. Zero personal data collected or transmitted.")
    print("💡 Press Ctrl+C to terminate the local server.")
    uvicorn.run("ultimate_travel_agent.web.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
