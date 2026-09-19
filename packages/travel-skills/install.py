#!/usr/bin/env python3
"""Cross-platform installer for Travel Skills Pack with local manifest tracking.

Copies travel skills, agents, and workflows into <target-project>/.agents/
without touching or overwriting existing files unless --force is specified.
Records all installed files in .agents/.ultimate-travel-agent-install.json for safe removal.
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path if running from repository
repo_src = Path(__file__).resolve().parent.parent.parent / "src"
if repo_src.exists():
    sys.path.insert(0, str(repo_src))

from ultimate_travel_agent.skills import install_pack_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Travel Skills Pack into an Antigravity project with manifest tracking."
    )
    parser.add_argument("--target", "-t", required=True, type=Path, help="Path to target project root.")
    parser.add_argument("--include-agents", action="store_true", help="Include 12 specialized agents.")
    parser.add_argument("--include-workflows", action="store_true", help="Include 9 travel workflows.")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation.")

    args = parser.parse_args()
    target_path = args.target.resolve()

    print(f"Installing Travel Skills Pack into: {target_path}")
    result = install_pack_skills(
        target_dir=target_path,
        include_agents=args.include_agents,
        include_workflows=args.include_workflows,
        force=args.force,
        dry_run=args.dry_run,
    )

    prefix = "[DRY-RUN] " if args.dry_run else ""
    if result["installed"]:
        print(f"\n{prefix}Successfully installed {len(result['installed'])} files.")
    if result["overwritten"]:
        print(f"{prefix}Overwritten with --force: {len(result['overwritten'])} files.")
    if result["skipped"]:
        print(f"{prefix}Skipped (already exists): {len(result['skipped'])} files (use --force to overwrite).")

    if result.get("manifest_path"):
        print(f"Installation manifest created at: {result['manifest_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
