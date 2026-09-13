#!/usr/bin/env python3
"""Cross-platform uninstaller for Travel Skills Pack.

Removes only the pack's internal skills from <target-project>/.agents/skills/
leaving any user-defined or third-party skills intact.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Ensure robust console output across all platforms and encodings
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass


def _can_encode(text: str) -> bool:
    """Check if stdout can encode the given string without error."""
    try:
        text.encode(sys.stdout.encoding or "ascii")
        return True
    except (UnicodeEncodeError, LookupError, AttributeError):
        return False


def get_pack_root() -> Path:
    """Return the root path of travel-skills package."""
    return Path(__file__).resolve().parent


def load_manifest(pack_root: Optional[Path] = None) -> dict:
    """Load package manifest.json."""
    root = pack_root or get_pack_root()
    manifest_file = root / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_file}")
    with open(manifest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def uninstall_skills(
    target_project: Path,
    pack_root: Optional[Path] = None,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    """Uninstall pack skills from target project's .agents/skills/ directory.

    Returns:
        Tuple of (removed_skills, not_found_skills)
    """
    root = pack_root or get_pack_root()
    manifest = load_manifest(root)

    target_skills_dir = target_project.resolve() / ".agents" / "skills"
    removed = []
    not_found = []

    for skill_info in manifest.get("skills", []):
        skill_name = skill_info["name"]
        dest_skill_dir = target_skills_dir / skill_name

        if dest_skill_dir.exists() and dest_skill_dir.is_dir():
            if not dry_run:
                shutil.rmtree(dest_skill_dir)
            removed.append(skill_name)
        else:
            not_found.append(skill_name)

    return removed, not_found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Uninstall Travel Skills Pack from an Antigravity project."
    )
    parser.add_argument(
        "--target",
        "-t",
        required=True,
        type=Path,
        help="Path to target project root directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate uninstallation without removing files.",
    )

    args = parser.parse_args()
    target_path = args.target.resolve()
    can_emoji = _can_encode("📦")
    ico_pack = "📦 " if can_emoji else ""
    ico_target = "🎯 " if can_emoji else ""
    ico_remove = "🗑️  " if can_emoji else "[REMOVED] "
    ico_info = "ℹ️  " if can_emoji else "[INFO] "
    ico_success = "✨ " if can_emoji else "[SUCCESS] "
    ico_err = "❌ " if can_emoji else "[ERROR] "
    bullet = "· " if can_emoji else "* "

    print(f"{ico_pack}Travel Skills Pack Uninstaller")
    print(f"{ico_target}Target project: {target_path}")

    try:
        removed, not_found = uninstall_skills(target_path, dry_run=args.dry_run)
    except Exception as exc:
        print(f"{ico_err}Error during uninstallation: {exc}", file=sys.stderr)
        return 1

    prefix = "[DRY-RUN] " if args.dry_run else ""
    if removed:
        print(f"\n{prefix}{ico_remove}Removed skills:")
        for s in removed:
            print(f"   - {s}")
    if not_found:
        print(f"\n{prefix}{ico_info}Skills not present in target project:")
        for s in not_found:
            print(f"   {bullet}{s}")

    if not removed:
        print(f"\n{ico_info}No matching travel pack skills were found in target project.")
    else:
        print(f"\n{ico_success}Uninstallation completed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
