#!/usr/bin/env python3
"""Cross-platform installer for Travel Skills Pack.

Copies internal travel skills into <target-project>/.agents/skills/
without touching or overwriting existing skills unless --force is specified.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple


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


def install_skills(
    target_project: Path,
    pack_root: Optional[Path] = None,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[List[str], List[str], List[str]]:
    """Install pack skills into target project's .agents/skills/ directory.

    Returns:
        Tuple of (installed_skills, skipped_skills, overwritten_skills)
    """
    root = pack_root or get_pack_root()
    manifest = load_manifest(root)
    skills_dir = root / "skills"

    target_skills_dir = target_project.resolve() / ".agents" / "skills"
    if not dry_run:
        target_skills_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    skipped = []
    overwritten = []

    for skill_info in manifest.get("skills", []):
        skill_name = skill_info["name"]
        src_skill_dir = skills_dir / skill_name
        dest_skill_dir = target_skills_dir / skill_name

        if not src_skill_dir.exists():
            continue

        if dest_skill_dir.exists():
            if not force:
                skipped.append(skill_name)
                continue
            else:
                if not dry_run:
                    shutil.rmtree(dest_skill_dir)
                    shutil.copytree(src_skill_dir, dest_skill_dir)
                overwritten.append(skill_name)
        else:
            if not dry_run:
                shutil.copytree(src_skill_dir, dest_skill_dir)
            installed.append(skill_name)

    return installed, skipped, overwritten


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Travel Skills Pack into an Antigravity project."
    )
    parser.add_argument(
        "--target",
        "-t",
        required=True,
        type=Path,
        help="Path to target project root directory.",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite skills that already exist in target project.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate installation without modifying files.",
    )

    args = parser.parse_args()

    target_path = args.target.resolve()
    print(f"📦 Travel Skills Pack Installer")
    print(f"🎯 Target project: {target_path}")

    try:
        installed, skipped, overwritten = install_skills(
            target_project=target_path,
            force=args.force,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        print(f"❌ Error during installation: {exc}", file=sys.stderr)
        return 1

    prefix = "[DRY-RUN] " if args.dry_run else ""
    if installed:
        print(f"\n{prefix}✅ Installed skills:")
        for s in installed:
            print(f"   + {s}")
    if overwritten:
        print(f"\n{prefix}🔄 Overwritten skills (--force):")
        for s in overwritten:
            print(f"   ~ {s}")
    if skipped:
        print(f"\n{prefix}⚠️  Skipped existing skills (use --force to overwrite):")
        for s in skipped:
            print(f"   - {s}")

    if not installed and not overwritten:
        if skipped:
            print("\nℹ️  All skills were already present. Nothing changed.")
        else:
            print("\n⚠️  No skills found in package to install.")
    else:
        print(f"\n✨ Successfully finished. Target skills directory: {target_path / '.agents' / 'skills'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
