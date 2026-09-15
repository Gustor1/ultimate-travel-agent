"""CLI entry point for ultimate-travel-agent Skills-First pack."""

import argparse
import os
import shutil
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Resolve repository root or package base directory."""
    current = Path(__file__).resolve().parent
    repo_root = current.parent.parent
    if (repo_root / ".agents").exists():
        return repo_root
    if (Path.cwd() / ".agents").exists():
        return Path.cwd()
    return repo_root


def copy_directory(src_dir: Path, dest_dir: Path, force: bool, installed_files: list):
    """Recursively copy files from src_dir to dest_dir with overwrite protection."""
    if not src_dir.exists():
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    for item in src_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src_dir)
            target_file = dest_dir / rel_path

            if target_file.exists() and not force:
                print(f"Skipping {target_file} (already exists, use --force to overwrite)")
                continue

            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
            installed_files.append(target_file)
            print(f"Installed: {target_file}")


def install_skills(args):
    """Install travel skills into target project."""
    target = Path(args.target).resolve()
    base_dir = get_base_dir()

    installed_files = []

    # 1. Install skills
    skills_src = base_dir / "packages" / "travel-skills" / "skills"
    if not skills_src.exists():
        skills_src = base_dir / ".agents" / "skills"

    skills_dest = target / ".agents" / "skills"
    copy_directory(skills_src, skills_dest, args.force, installed_files)

    # 2. Install agents
    if getattr(args, "include_agents", False):
        agents_src = base_dir / ".agents" / "agents"
        if agents_src.exists():
            agents_dest = target / ".agents" / "agents"
            copy_directory(agents_src, agents_dest, args.force, installed_files)

    # 3. Install workflows
    if getattr(args, "include_workflows", False):
        workflows_src = base_dir / ".agents" / "workflows"
        if workflows_src.exists():
            workflows_dest = target / ".agents" / "workflows"
            copy_directory(workflows_src, workflows_dest, args.force, installed_files)

    print(f"\nSummary: {len(installed_files)} files installed successfully into {target}.")


def uninstall_skills(args):
    """Uninstall travel skills and components from target project."""
    target = Path(args.target).resolve()

    skills_dest = target / ".agents" / "skills"
    if skills_dest.exists():
        shutil.rmtree(skills_dest)
        print(f"Removed skills: {skills_dest}")

    agents_dest = target / ".agents" / "agents"
    if agents_dest.exists():
        shutil.rmtree(agents_dest)
        print(f"Removed agents: {agents_dest}")

    workflows_dest = target / ".agents" / "workflows"
    if workflows_dest.exists():
        shutil.rmtree(workflows_dest)
        print(f"Removed workflows: {workflows_dest}")

    print(f"\nSummary: Uninstalled travel skills from {target}")


def list_skills(args):
    """List available travel skills."""
    base_dir = get_base_dir()
    skills_dir = base_dir / "packages" / "travel-skills" / "skills"
    if not skills_dir.exists():
        skills_dir = base_dir / ".agents" / "skills"

    if not skills_dir.exists():
        print("No skills directory found.")
        return

    print("Available Travel Skills:")
    for s in sorted(skills_dir.iterdir()):
        if s.is_dir() and (s / "SKILL.md").exists():
            print(f"  - {s.name}")


def main():
    parser = argparse.ArgumentParser(description="Ultimate Travel Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install-skills", help="Install travel skills into a project")
    install_parser.add_argument("--target", "-t", required=True, help="Target project path")
    install_parser.add_argument("--include-agents", action="store_true", help="Include sub-agents")
    install_parser.add_argument("--include-workflows", action="store_true", help="Include workflows")
    install_parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files")

    uninstall_parser = subparsers.add_parser("uninstall-skills", help="Uninstall travel skills from a project")
    uninstall_parser.add_argument("--target", "-t", required=True, help="Target project path")

    list_parser = subparsers.add_parser("list-skills", help="List available travel skills")

    args = parser.parse_args()

    if args.command == "install-skills":
        install_skills(args)
    elif args.command == "uninstall-skills":
        uninstall_skills(args)
    elif args.command == "list-skills":
        list_skills(args)


if __name__ == "__main__":
    main()
