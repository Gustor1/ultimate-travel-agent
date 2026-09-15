"""Skills management utilities for packaging, installing, listing, and uninstalling travel skills.

Implements manifest-based installation tracking to guarantee non-destructive, safe uninstallation
without affecting custom user skills, agents, or workflows.
"""

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

MANIFEST_FILE_NAME = ".ultimate-travel-agent-install.json"
PACK_VERSION = "1.2.0"
PACK_NAME = "ultimate-travel-agent"


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_install_manifest_path(target_dir: Path) -> Path:
    """Return path to the local installation manifest in target project."""
    return target_dir.resolve() / ".agents" / MANIFEST_FILE_NAME


def load_install_manifest(target_dir: Path) -> Optional[Dict[str, Any]]:
    """Load local installation manifest if it exists."""
    manifest_path = get_install_manifest_path(target_dir)
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_install_manifest(target_dir: Path, manifest_data: Dict[str, Any]) -> Path:
    """Save installation manifest to target project's .agents directory."""
    manifest_path = get_install_manifest_path(target_dir)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    return manifest_path


def find_pack_root() -> Path:
    """Find travel-skills package directory in repository or package installation."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    local_pack = repo_root / "packages" / "travel-skills"
    if local_pack.exists() and (local_pack / "manifest.json").exists():
        return local_pack

    cwd_pack = Path.cwd() / "packages" / "travel-skills"
    if cwd_pack.exists() and (cwd_pack / "manifest.json").exists():
        return cwd_pack

    local_agents = repo_root / ".agents" / "skills"
    if local_agents.exists():
        return repo_root

    raise FileNotFoundError("Could not locate travel-skills package or repository root.")


def get_manifest(pack_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load the skills pack manifest."""
    root = pack_root or find_pack_root()
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    nested = root / "packages" / "travel-skills" / "manifest.json"
    if nested.exists():
        with open(nested, "r", encoding="utf-8") as f:
            return json.load(f)

    skills_dir = root / ".agents" / "skills"
    if skills_dir.exists():
        skills = []
        for s in sorted(skills_dir.iterdir()):
            if s.is_dir() and (s / "SKILL.md").exists():
                skills.append({
                    "name": s.name,
                    "description": f"Skill for {s.name}",
                    "path": f"skills/{s.name}/SKILL.md",
                })
        return {
            "name": "travel-skills",
            "version": PACK_VERSION,
            "description": "Travel skills pack",
            "skills": skills,
        }

    raise FileNotFoundError("Could not find skills manifest.")


def list_available_skills(pack_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return a list of available skills with metadata."""
    manifest = get_manifest(pack_root)
    return manifest.get("skills", [])


def copy_file_tracked(
    src_file: Path,
    dest_file: Path,
    force: bool,
    component: str,
    installed_files: Dict[str, Dict[str, str]],
    skipped_files: List[str],
    overwritten_files: List[str],
    target_root: Path,
    dry_run: bool = False,
):
    """Copy a single file while calculating sha256 and tracking in manifest records."""
    rel_dest = str(dest_file.relative_to(target_root)).replace("\\", "/")
    src_sha256 = compute_file_sha256(src_file)

    if dest_file.exists():
        if not force:
            skipped_files.append(rel_dest)
            return
        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)
        overwritten_files.append(rel_dest)
    else:
        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)

    installed_files[rel_dest] = {
        "sha256": src_sha256,
        "component": component,
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }


def copy_tree_tracked(
    src_dir: Path,
    dest_dir: Path,
    force: bool,
    component: str,
    installed_files: Dict[str, Dict[str, str]],
    skipped_files: List[str],
    overwritten_files: List[str],
    target_root: Path,
    dry_run: bool = False,
):
    """Recursively copy files with hash tracking and collision protection."""
    if not src_dir.exists():
        return

    for item in src_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src_dir)
            target_file = dest_dir / rel_path
            copy_file_tracked(
                src_file=item,
                dest_file=target_file,
                force=force,
                component=component,
                installed_files=installed_files,
                skipped_files=skipped_files,
                overwritten_files=overwritten_files,
                target_root=target_root,
                dry_run=dry_run,
            )


def install_pack_skills(
    target_dir: Path,
    pack_root: Optional[Path] = None,
    include_agents: bool = False,
    include_workflows: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Install travel skills, agents, and workflows into target project with manifest tracking."""
    target_dir = target_dir.resolve()
    repo_root = find_pack_root()
    if (repo_root / "packages" / "travel-skills").exists():
        base_dir = repo_root
    else:
        base_dir = repo_root.parent.parent if repo_root.name == "travel-skills" else repo_root

    existing_manifest = load_install_manifest(target_dir) or {}
    files_registry: Dict[str, Dict[str, str]] = existing_manifest.get("files", {})
    installed_skills_set: Set[str] = set(existing_manifest.get("installed_skills", []))
    installed_agents_set: Set[str] = set(existing_manifest.get("installed_agents", []))
    installed_workflows_set: Set[str] = set(existing_manifest.get("installed_workflows", []))

    newly_installed: Dict[str, Dict[str, str]] = {}
    skipped_files: List[str] = []
    overwritten_files: List[str] = []

    # 1. Install Skills
    skills_src = base_dir / "packages" / "travel-skills" / "skills"
    if not skills_src.exists():
        skills_src = base_dir / ".agents" / "skills"

    if skills_src.exists():
        for skill_dir in sorted(skills_src.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                dest_skill_dir = target_dir / ".agents" / "skills" / skill_dir.name
                copy_tree_tracked(
                    src_dir=skill_dir,
                    dest_dir=dest_skill_dir,
                    force=force,
                    component="skill",
                    installed_files=newly_installed,
                    skipped_files=skipped_files,
                    overwritten_files=overwritten_files,
                    target_root=target_dir,
                    dry_run=dry_run,
                )
                installed_skills_set.add(skill_dir.name)

    # 2. Install Agents
    if include_agents:
        agents_src = base_dir / ".agents" / "agents"
        if agents_src.exists():
            for agent_dir in sorted(agents_src.iterdir()):
                if agent_dir.is_dir() and (agent_dir / "agent.md").exists():
                    dest_agent_dir = target_dir / ".agents" / "agents" / agent_dir.name
                    copy_tree_tracked(
                        src_dir=agent_dir,
                        dest_dir=dest_agent_dir,
                        force=force,
                        component="agent",
                        installed_files=newly_installed,
                        skipped_files=skipped_files,
                        overwritten_files=overwritten_files,
                        target_root=target_dir,
                        dry_run=dry_run,
                    )
                    installed_agents_set.add(agent_dir.name)

    # 3. Install Workflows
    if include_workflows:
        workflows_src = base_dir / ".agents" / "workflows"
        if workflows_src.exists():
            for wf_file in sorted(workflows_src.iterdir()):
                if wf_file.is_file() and wf_file.suffix == ".md":
                    dest_wf_file = target_dir / ".agents" / "workflows" / wf_file.name
                    copy_file_tracked(
                        src_file=wf_file,
                        dest_file=dest_wf_file,
                        force=force,
                        component="workflow",
                        installed_files=newly_installed,
                        skipped_files=skipped_files,
                        overwritten_files=overwritten_files,
                        target_root=target_dir,
                        dry_run=dry_run,
                    )
                    installed_workflows_set.add(wf_file.name)

    files_registry.update(newly_installed)

    manifest_data = {
        "pack_name": PACK_NAME,
        "pack_version": PACK_VERSION,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "installed_skills": sorted(list(installed_skills_set)),
        "installed_agents": sorted(list(installed_agents_set)),
        "installed_workflows": sorted(list(installed_workflows_set)),
        "files": files_registry,
    }

    manifest_path = None
    if not dry_run and files_registry:
        manifest_path = save_install_manifest(target_dir, manifest_data)

    return {
        "installed": list(newly_installed.keys()),
        "skipped": skipped_files,
        "overwritten": overwritten_files,
        "manifest_path": manifest_path,
        "skills_count": len(installed_skills_set),
        "agents_count": len(installed_agents_set),
        "workflows_count": len(installed_workflows_set),
    }


def clean_empty_parents(path: Path, stop_at: Path):
    """Remove empty parent directories up to stop_at (exclusive)."""
    curr = path
    while curr != stop_at and curr.exists() and curr.is_dir():
        try:
            if not any(curr.iterdir()):
                curr.rmdir()
                curr = curr.parent
            else:
                break
        except OSError:
            break


def uninstall_pack_skills(
    target_dir: Path,
    force: bool = False,
    clean_modified: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Uninstall only the files registered in the local installation manifest."""
    target_dir = target_dir.resolve()
    manifest_data = load_install_manifest(target_dir)

    removed_files: List[str] = []
    skipped_modified: List[str] = []
    not_found: List[str] = []
    remaining_files: Dict[str, Dict[str, str]] = {}

    if manifest_data and "files" in manifest_data:
        tracked_files = manifest_data["files"]
        for rel_path, file_meta in tracked_files.items():
            full_path = target_dir / rel_path
            recorded_sha = file_meta.get("sha256")

            if not full_path.exists():
                not_found.append(rel_path)
                continue

            current_sha = compute_file_sha256(full_path)
            is_modified = recorded_sha and (current_sha != recorded_sha)

            if is_modified and not (force or clean_modified):
                skipped_modified.append(rel_path)
                remaining_files[rel_path] = file_meta
                continue

            if not dry_run:
                try:
                    full_path.unlink()
                    removed_files.append(rel_path)
                    clean_empty_parents(full_path.parent, target_dir / ".agents")
                except Exception as e:
                    skipped_modified.append(f"{rel_path} (error: {e})")
            else:
                removed_files.append(rel_path)

        manifest_path = get_install_manifest_path(target_dir)
        if not dry_run:
            if remaining_files:
                manifest_data["files"] = remaining_files
                save_install_manifest(target_dir, manifest_data)
            else:
                if manifest_path.exists():
                    manifest_path.unlink()
                clean_empty_parents(target_dir / ".agents", target_dir)

    else:
        agents_root = target_dir / ".agents"
        if agents_root.exists():
            known_skills = [
                "travel-orchestrator", "travel-web-research", "transport-research",
                "accommodation-research", "activity-curator", "local-discovery",
                "itinerary-builder", "budget-and-booking-checker", "travel-safety",
                "source-verification", "travel-quality-control", "multi-agent-orchestration",
                "mcp-skill-auditing"
            ]
            skills_dir = agents_root / "skills"
            if skills_dir.exists():
                for s in known_skills:
                    s_path = skills_dir / s
                    if s_path.exists() and s_path.is_dir():
                        if not dry_run:
                            shutil.rmtree(s_path, ignore_errors=True)
                        removed_files.append(f".agents/skills/{s}")

            if not dry_run:
                clean_empty_parents(skills_dir, target_dir)
                clean_empty_parents(agents_root, target_dir)

    return {
        "removed": removed_files,
        "skipped_modified": skipped_modified,
        "not_found": not_found,
        "manifest_cleaned": (len(remaining_files) == 0),
    }
