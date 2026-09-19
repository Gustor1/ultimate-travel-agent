#!/usr/bin/env python3
"""Cross-platform uninstaller for Travel Skills Pack with manifest-based safety.

Deletes ONLY files recorded in .agents/.ultimate-travel-agent-install.json.
Never touches custom user skills, agents, or workflows.
Preserves files modified by the user unless --clean-modified or --force is supplied.
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path if running from repository
repo_src = Path(__file__).resolve().parent.parent.parent / "src"
if repo_src.exists():
    sys.path.insert(0, str(repo_src))

from ultimate_travel_agent.skills import uninstall_pack_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely uninstall Travel Skills Pack using the local installation manifest."
    )
    parser.add_argument("--target", "-t", required=True, type=Path, help="Path to target project root.")
    parser.add_argument("--force", "-f", action="store_true", help="Delete even if files were modified.")
    parser.add_argument("--clean-modified", action="store_true", help="Delete user-modified files.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate uninstallation.")

    args = parser.parse_args()
    target_path = args.target.resolve()

    print(f"Uninstalling Travel Skills Pack from: {target_path}")
    result = uninstall_pack_skills(
        target_dir=target_path,
        force=args.force,
        clean_modified=args.clean_modified,
        dry_run=args.dry_run,
    )

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{prefix}Removed {len(result['removed'])} files.")

    if result["skipped_modified"]:
        print(f"\n[WARNING] Preserved {len(result['skipped_modified'])} user-modified files:")
        for f in result["skipped_modified"]:
            print(f"   ! {f}")
        print("Use --clean-modified or --force if you wish to remove these modified files.")

    if result.get("manifest_cleaned"):
        print("Installation manifest removed.")
    else:
        print("Installation manifest updated with remaining files.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
