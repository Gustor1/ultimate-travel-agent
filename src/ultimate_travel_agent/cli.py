"""CLI entry point for ultimate-travel-agent Skills-First pack."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from ultimate_travel_agent.skills import (
    find_pack_root,
    install_pack_skills,
    list_available_skills,
    sync_pack_mirror,
    uninstall_pack_skills,
)


def install_skills_cmd(args: argparse.Namespace) -> None:
    target = Path(args.target).resolve()
    print(f"Installing Ultimate Travel Agent pack into: {target}")
    result = install_pack_skills(
        target_dir=target,
        include_agents=getattr(args, "include_agents", False),
        include_workflows=getattr(args, "include_workflows", False),
        force=getattr(args, "force", False),
        dry_run=getattr(args, "dry_run", False),
    )

    prefix = "[DRY-RUN] " if getattr(args, "dry_run", False) else ""
    if result["installed"]:
        print(f"\n{prefix}Installed files ({len(result['installed'])}):")
        for f in result["installed"][:15]:
            print(f"   + {f}")
        if len(result["installed"]) > 15:
            print(f"   ... and {len(result['installed']) - 15} more files.")

    if result["overwritten"]:
        print(f"\n{prefix}Overwritten files (--force, {len(result['overwritten'])}):")
        for f in result["overwritten"][:10]:
            print(f"   ~ {f}")

    if result["skipped"]:
        print(
            f"\n{prefix}Skipped existing files ({len(result['skipped'])} - use --force to overwrite):"
        )
        for f in result["skipped"][:10]:
            print(f"   - {f}")

    print(
        f"\nSummary: {len(result['installed'])} files installed. Target skills: {result['skills_count']}, agents: {result['agents_count']}, workflows: {result['workflows_count']}."
    )
    if result.get("manifest_path"):
        print(f"Manifest written to: {result['manifest_path']}")


def uninstall_skills_cmd(args: argparse.Namespace) -> None:
    target = Path(args.target).resolve()
    print(f"Uninstalling Ultimate Travel Agent pack from: {target}")
    result = uninstall_pack_skills(
        target_dir=target,
        force=getattr(args, "force", False),
        clean_modified=getattr(args, "clean_modified", False),
        dry_run=getattr(args, "dry_run", False),
    )

    prefix = "[DRY-RUN] " if getattr(args, "dry_run", False) else ""
    if result["removed"]:
        print(f"\n{prefix}Removed files ({len(result['removed'])}):")
        for f in result["removed"][:15]:
            print(f"   - {f}")
        if len(result["removed"]) > 15:
            print(f"   ... and {len(result['removed']) - 15} more files.")

    if result.get("restored"):
        print(f"\nRestored pre-existing files ({len(result['restored'])}):")
        for f in result["restored"]:
            print(f"   = {f}")

    if result["skipped_modified"]:
        print(f"\n[WARNING] Skipped user-modified files ({len(result['skipped_modified'])}):")
        for f in result["skipped_modified"]:
            print(f"   ! {f} (modified after install; use --clean-modified or --force to delete)")

    if result["not_found"]:
        print(f"\nAlready removed or missing ({len(result['not_found'])} files).")

    if result.get("errors"):
        print("\n[ERROR] Uninstallation did not remove untracked or unsafe files:")
        for error in result["errors"]:
            print(f"   ! {error}")

    status = (
        "Manifest cleaned."
        if result.get("manifest_cleaned")
        else "Manifest updated with remaining files."
    )
    print(f"\nSummary: {len(result['removed'])} files removed. {status}")


def list_skills_cmd(args: argparse.Namespace) -> None:
    skills = list_available_skills()
    print(f"Available Travel Skills ({len(skills)}):")
    for s in skills:
        desc = s.get("description", "")
        print(f"  - {s['name']}: {desc}")


def validate_skills_cmd(args: argparse.Namespace) -> None:
    from ultimate_travel_agent.validator import validate_all_skills

    pack_dir = Path(args.path).resolve() if getattr(args, "path", None) else None
    passed, reports = validate_all_skills(pack_dir)
    print(f"Skill Quality Validation: {'PASSED' if passed else 'FAILED'}")
    for skill_name, issues in reports.items():
        if issues:
            print(f"  [FAIL] {skill_name}:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"  [OK]   {skill_name}")
    if not passed:
        sys.exit(1)


def validate_dossier_cmd(args: argparse.Namespace) -> None:
    """Validate JSON or YAML against the TravelDossier v1 contract."""
    from ultimate_travel_agent.contracts import validate_travel_dossier

    dossier_path = Path(args.path).resolve()
    raw = dossier_path.read_text(encoding="utf-8")
    data = json.loads(raw) if dossier_path.suffix.lower() == ".json" else yaml.safe_load(raw)
    if not isinstance(data, dict):
        print("Travel dossier must contain a top-level object.")
        raise SystemExit(1)
    passed, issues, dossier = validate_travel_dossier(data)
    print(f"TravelDossier v1: {'PASSED' if passed else 'FAILED'}")
    if dossier is not None:
        print(
            f"Mode: {dossier.mode}; claims: {len(dossier.claims)}; "
            f"sources: {len(dossier.sources)}; booking-ready: {dossier.readiness.booking_ready}"
        )
    for issue in issues:
        print(f"  - {issue}")
    if not passed:
        raise SystemExit(1)


def sync_pack_cmd(args: argparse.Namespace) -> None:
    """Generate or verify the compatibility mirror."""
    result = sync_pack_mirror(check=args.check)
    if args.check and result["out_of_sync"]:
        print("Pack mirror is out of sync:")
        for path in result["out_of_sync"]:
            print(f"  - {path}")
        raise SystemExit(1)
    if result["changed"]:
        print(f"Synchronized {len(result['changed'])} files.")
    else:
        print("Pack mirror is synchronized.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ultimate Travel Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser(
        "install-skills", help="Install travel skills into a project"
    )
    install_parser.add_argument("--target", "-t", required=True, help="Target project path")
    install_parser.add_argument("--include-agents", action="store_true", help="Include sub-agents")
    install_parser.add_argument(
        "--include-workflows", action="store_true", help="Include workflows"
    )
    install_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files"
    )
    install_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate installation without touching files"
    )

    uninstall_parser = subparsers.add_parser(
        "uninstall-skills", help="Uninstall travel skills from a project"
    )
    uninstall_parser.add_argument("--target", "-t", required=True, help="Target project path")
    uninstall_parser.add_argument(
        "--force", "-f", action="store_true", help="Remove even if files were modified"
    )
    uninstall_parser.add_argument(
        "--clean-modified", action="store_true", help="Remove user-modified files"
    )
    uninstall_parser.add_argument("--dry-run", action="store_true", help="Simulate uninstallation")

    subparsers.add_parser("list-skills", help="List available travel skills")

    val_parser = subparsers.add_parser(
        "validate-skills", help="Validate quality and standards of travel skills"
    )
    val_parser.add_argument("--path", "-p", help="Optional path to skills folder")

    dossier_parser = subparsers.add_parser(
        "validate-dossier", help="Validate a JSON/YAML TravelDossier v1 file"
    )
    dossier_parser.add_argument("path", help="Path to a JSON or YAML dossier")

    sync_parser = subparsers.add_parser(
        "sync-pack", help="Generate the compatibility skill mirror from canonical .agents assets"
    )
    sync_parser.add_argument(
        "--check", action="store_true", help="Fail if the mirror is out of sync"
    )

    args = parser.parse_args()

    if args.command == "install-skills":
        install_skills_cmd(args)
    elif args.command == "uninstall-skills":
        uninstall_skills_cmd(args)
    elif args.command == "list-skills":
        list_skills_cmd(args)
    elif args.command == "validate-skills":
        validate_skills_cmd(args)
    elif args.command == "validate-dossier":
        validate_dossier_cmd(args)
    elif args.command == "sync-pack":
        sync_pack_cmd(args)


if __name__ == "__main__":
    main()

# Backward compatibility aliases for CLI functions and tests
install_skills = install_skills_cmd
uninstall_skills = uninstall_skills_cmd


def get_base_dir() -> Path:
    """Return repository or pack base directory."""
    root = find_pack_root()
    if root.name == ".agents":
        return root.parent
    return root.parent if root.name == "bundle" else root
