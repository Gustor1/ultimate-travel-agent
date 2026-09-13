"""Skills management utilities for packaging, installing, and listing travel skills."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_pack_root() -> Path:
    """Find travel-skills package directory in repository or package installation."""
    # Check relative to this module in source tree
    repo_root = Path(__file__).resolve().parent.parent.parent
    local_pack = repo_root / "packages" / "travel-skills"
    if local_pack.exists() and (local_pack / "manifest.json").exists():
        return local_pack

    # Check current working directory
    cwd_pack = Path.cwd() / "packages" / "travel-skills"
    if cwd_pack.exists() and (cwd_pack / "manifest.json").exists():
        return cwd_pack

    # Fallback to internal .agents/skills in repo
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

    # If root is repo root without manifest in root, check packages/travel-skills
    nested = root / "packages" / "travel-skills" / "manifest.json"
    if nested.exists():
        with open(nested, "r", encoding="utf-8") as f:
            return json.load(f)

    # Generate synthetic manifest from .agents/skills if needed
    skills_dir = root / ".agents" / "skills"
    if skills_dir.exists():
        skills = []
        for s in sorted(skills_dir.iterdir()):
            if s.is_dir() and (s / "SKILL.md").exists():
                skills.append({"name": s.name, "description": f"Skill {s.name}", "path": f"skills/{s.name}/SKILL.md"})
        return {
            "name": "travel-skills",
            "version": "1.0.0",
            "description": "Travel skills pack",
            "skills": skills,
        }

    raise FileNotFoundError("Could not find skills manifest.")


def list_available_skills(pack_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return a list of available skills with metadata."""
    manifest = get_manifest(pack_root)
    return manifest.get("skills", [])


def install_pack_skills(
    target_dir: Path,
    pack_root: Optional[Path] = None,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[List[str], List[str], List[str]]:
    """Install pack skills into target directory's .agents/skills/.

    Returns:
        Tuple of (installed, skipped, overwritten)
    """
    root = pack_root or find_pack_root()
    manifest = get_manifest(root)

    # Determine source skills dir
    if (root / "skills").exists():
        src_skills_dir = root / "skills"
    elif (root / "packages" / "travel-skills" / "skills").exists():
        src_skills_dir = root / "packages" / "travel-skills" / "skills"
    elif (root / ".agents" / "skills").exists():
        src_skills_dir = root / ".agents" / "skills"
    else:
        raise FileNotFoundError(f"Source skills directory not found in {root}")

    dest_skills_dir = target_dir.resolve() / ".agents" / "skills"
    if not dry_run:
        dest_skills_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    skipped = []
    overwritten = []

    for item in manifest.get("skills", []):
        name = item["name"]
        src = src_skills_dir / name
        dest = dest_skills_dir / name

        if not src.exists():
            continue

        if dest.exists():
            if not force:
                skipped.append(name)
                continue
            else:
                if not dry_run:
                    shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                overwritten.append(name)
        else:
            if not dry_run:
                shutil.copytree(src, dest)
            installed.append(name)

    return installed, skipped, overwritten


def uninstall_pack_skills(
    target_dir: Path,
    pack_root: Optional[Path] = None,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    """Uninstall pack skills from target directory's .agents/skills/.

    Returns:
        Tuple of (removed, not_found)
    """
    root = pack_root or find_pack_root()
    manifest = get_manifest(root)

    dest_skills_dir = target_dir.resolve() / ".agents" / "skills"
    removed = []
    not_found = []

    for item in manifest.get("skills", []):
        name = item["name"]
        dest = dest_skills_dir / name

        if dest.exists() and dest.is_dir():
            if not dry_run:
                shutil.rmtree(dest)
            removed.append(name)
        else:
            not_found.append(name)

    return removed, not_found
