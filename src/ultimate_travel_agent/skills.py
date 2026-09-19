"""Safe packaging, installation, mirroring, and removal of travel assets."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

from ultimate_travel_agent import __version__

MANIFEST_FILE_NAME = ".ultimate-travel-agent-install.json"
PACK_VERSION = __version__
PACK_NAME = "ultimate-travel-agent"


class ManifestError(ValueError):
    """Raised when an installation or bundle manifest cannot be trusted."""


def compute_file_sha256(filepath: Path) -> str:
    """Compute a SHA-256 digest without loading a complete file in memory."""

    hasher = hashlib.sha256()
    with filepath.open("rb") as handle:
        while chunk := handle.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _safe_join(root: Path, relative_path: str | Path) -> Path:
    """Resolve a relative path and reject traversal, absolute paths, and escaping links."""

    root_resolved = root.resolve()
    raw = Path(relative_path)
    if raw.is_absolute() or ".." in raw.parts:
        raise ManifestError(f"Unsafe path outside target root: {relative_path}")
    candidate = (root_resolved / raw).resolve(strict=False)
    if not _is_relative_to(candidate, root_resolved):
        raise ManifestError(f"Unsafe path outside target root: {relative_path}")
    return candidate


def get_install_manifest_path(target_dir: Path) -> Path:
    return target_dir.resolve() / ".agents" / MANIFEST_FILE_NAME


def load_install_manifest(target_dir: Path) -> dict[str, Any] | None:
    """Load and minimally validate a local manifest; malformed data fails closed."""

    manifest_path = get_install_manifest_path(target_dir)
    if not manifest_path.exists():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Invalid installation manifest: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise ManifestError("Invalid installation manifest: expected an object with a files map")
    for relative_path, metadata in data["files"].items():
        _safe_join(target_dir, relative_path)
        if not isinstance(metadata, dict) or not isinstance(metadata.get("sha256"), str):
            raise ManifestError(f"Invalid manifest metadata for {relative_path}")
    return data


def save_install_manifest(target_dir: Path, manifest_data: dict[str, Any]) -> Path:
    """Atomically save the installation manifest in the target project."""

    manifest_path = get_install_manifest_path(target_dir)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=manifest_path.parent, delete=False, suffix=".tmp"
        ) as handle:
            json.dump(manifest_data, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, manifest_path)
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()
    return manifest_path


def find_pack_root() -> Path:
    """Find canonical assets in a checkout or in the installed wheel."""

    repository_root = Path(__file__).resolve().parent.parent.parent
    repository_bundle = repository_root / ".agents"
    if (repository_bundle / "manifest.json").exists():
        return repository_bundle

    working_bundle = Path.cwd() / ".agents"
    if (working_bundle / "manifest.json").exists():
        return working_bundle

    try:
        installed_bundle = Path(str(files("ultimate_travel_agent.bundle"))).resolve()
    except (ImportError, ModuleNotFoundError, TypeError) as exc:
        raise FileNotFoundError("Could not locate bundled travel assets") from exc
    if not (installed_bundle / "manifest.json").exists():
        raise FileNotFoundError("Installed travel bundle is missing manifest.json")
    return installed_bundle


def get_manifest(pack_root: Path | None = None) -> dict[str, Any]:
    root = (pack_root or find_pack_root()).resolve()
    candidates = [root / "manifest.json", root / ".agents" / "manifest.json"]
    manifest_path = next((candidate for candidate in candidates if candidate.exists()), None)
    if manifest_path is None:
        raise FileNotFoundError(f"Could not find bundle manifest below {root}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Invalid bundle manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("version") != PACK_VERSION:
        raise ManifestError(
            f"Bundle version must match package version {PACK_VERSION}: {manifest.get('version')}"
        )
    for collection in ("skills", "agents", "workflows"):
        entries = manifest.get(collection, [])
        if not isinstance(entries, list):
            raise ManifestError(f"Bundle manifest field {collection} must be a list")
        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("name") or not entry.get("path"):
                raise ManifestError(f"Invalid {collection} entry in bundle manifest")
            source = _safe_join(root, str(entry["path"]))
            if not source.is_file():
                raise ManifestError(f"Manifest references missing file: {entry['path']}")
    return manifest


def list_available_skills(pack_root: Path | None = None) -> list[dict[str, Any]]:
    return list(get_manifest(pack_root).get("skills", []))


def _backup_existing_file(
    dest_file: Path,
    relative_destination: str,
    target_root: Path,
    previous_metadata: dict[str, str] | None,
    dry_run: bool,
) -> str | None:
    if previous_metadata and previous_metadata.get("backup_path"):
        return previous_metadata["backup_path"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_relative = f".agents/.ultimate-travel-agent-backups/{stamp}/{relative_destination}"
    backup_path = _safe_join(target_root, backup_relative)
    if not dry_run:
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest_file, backup_path, follow_symlinks=False)
    return backup_relative


def copy_file_tracked(
    src_file: Path,
    dest_file: Path,
    force: bool,
    component: str,
    installed_files: dict[str, dict[str, str]],
    skipped_files: list[str],
    overwritten_files: list[str],
    target_root: Path,
    dry_run: bool = False,
    previous_metadata: dict[str, str] | None = None,
) -> None:
    """Copy one trusted bundle file with collision protection and restoration metadata."""

    target_root = target_root.resolve()
    destination = dest_file.resolve(strict=False)
    if not _is_relative_to(destination, target_root):
        raise ManifestError(f"Destination escapes target root: {dest_file}")
    relative_destination = destination.relative_to(target_root).as_posix()
    source_hash = compute_file_sha256(src_file)
    backup_relative: str | None = None

    if dest_file.exists() or dest_file.is_symlink():
        if dest_file.is_symlink():
            raise ManifestError(f"Refusing to overwrite symbolic link: {relative_destination}")
        if not force:
            skipped_files.append(relative_destination)
            return
        current_hash = compute_file_sha256(dest_file)
        needs_backup = (
            previous_metadata is None
            or bool(previous_metadata.get("backup_path"))
            or current_hash != previous_metadata.get("sha256")
        )
        if needs_backup:
            backup_relative = _backup_existing_file(
                dest_file, relative_destination, target_root, previous_metadata, dry_run
            )
        overwritten_files.append(relative_destination)

    if not dry_run:
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file, follow_symlinks=False)

    metadata = {
        "sha256": source_hash,
        "component": component,
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }
    if backup_relative:
        metadata["backup_path"] = backup_relative
    installed_files[relative_destination] = metadata


def _install_entries(
    entries: list[dict[str, Any]],
    bundle_root: Path,
    target_root: Path,
    force: bool,
    component: str,
    existing_files: dict[str, dict[str, str]],
    installed_files: dict[str, dict[str, str]],
    skipped_files: list[str],
    overwritten_files: list[str],
    dry_run: bool,
) -> set[str]:
    installed_names: set[str] = set()
    for entry in entries:
        source = _safe_join(bundle_root, str(entry["path"]))
        relative_destination = f".agents/{entry['path']}"
        destination = _safe_join(target_root, relative_destination)
        copy_file_tracked(
            src_file=source,
            dest_file=destination,
            force=force,
            component=component,
            installed_files=installed_files,
            skipped_files=skipped_files,
            overwritten_files=overwritten_files,
            target_root=target_root,
            dry_run=dry_run,
            previous_metadata=existing_files.get(relative_destination),
        )
        if relative_destination in installed_files or relative_destination in existing_files:
            installed_names.add(str(entry["name"]))
    return installed_names


def install_pack_skills(
    target_dir: Path,
    pack_root: Path | None = None,
    include_agents: bool = False,
    include_workflows: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Install only manifest-listed assets into a target project."""

    target_root = target_dir.resolve()
    bundle_root = (pack_root or find_pack_root()).resolve()
    if (bundle_root / ".agents" / "manifest.json").exists():
        bundle_root = bundle_root / ".agents"
    manifest = get_manifest(bundle_root)
    existing_manifest = load_install_manifest(target_root) or {"files": {}}
    existing_files: dict[str, dict[str, str]] = existing_manifest.get("files", {})
    newly_installed: dict[str, dict[str, str]] = {}
    skipped_files: list[str] = []
    overwritten_files: list[str] = []

    installed_skills = set(existing_manifest.get("installed_skills", []))
    installed_agents = set(existing_manifest.get("installed_agents", []))
    installed_workflows = set(existing_manifest.get("installed_workflows", []))

    installed_skills.update(
        _install_entries(
            manifest["skills"],
            bundle_root,
            target_root,
            force,
            "skill",
            existing_files,
            newly_installed,
            skipped_files,
            overwritten_files,
            dry_run,
        )
    )
    if include_agents:
        installed_agents.update(
            _install_entries(
                manifest["agents"],
                bundle_root,
                target_root,
                force,
                "agent",
                existing_files,
                newly_installed,
                skipped_files,
                overwritten_files,
                dry_run,
            )
        )
    if include_workflows:
        installed_workflows.update(
            _install_entries(
                manifest["workflows"],
                bundle_root,
                target_root,
                force,
                "workflow",
                existing_files,
                newly_installed,
                skipped_files,
                overwritten_files,
                dry_run,
            )
        )

    files_registry = dict(existing_files)
    files_registry.update(newly_installed)
    manifest_data = {
        "manifest_schema": 2,
        "pack_name": PACK_NAME,
        "pack_version": PACK_VERSION,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "installed_skills": sorted(installed_skills),
        "installed_agents": sorted(installed_agents),
        "installed_workflows": sorted(installed_workflows),
        "files": files_registry,
    }

    manifest_path: Path | None = None
    if not dry_run and files_registry:
        manifest_path = save_install_manifest(target_root, manifest_data)

    return {
        "installed": list(newly_installed),
        "skipped": skipped_files,
        "overwritten": overwritten_files,
        "manifest_path": manifest_path,
        "skills_count": len(installed_skills),
        "agents_count": len(installed_agents),
        "workflows_count": len(installed_workflows),
    }


def clean_empty_parents(path: Path, stop_at: Path) -> None:
    current = path.resolve(strict=False)
    stop = stop_at.resolve(strict=False)
    while (
        current != stop and _is_relative_to(current, stop) and current.exists() and current.is_dir()
    ):
        try:
            if any(current.iterdir()):
                break
            current.rmdir()
            current = current.parent
        except OSError:
            break


def uninstall_pack_skills(
    target_dir: Path,
    force: bool = False,
    clean_modified: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Remove only validated manifest entries; missing manifests never trigger guessed deletion."""

    target_root = target_dir.resolve()
    manifest_data = load_install_manifest(target_root)
    if manifest_data is None:
        return {
            "removed": [],
            "restored": [],
            "skipped_modified": [],
            "not_found": [],
            "errors": ["No installation manifest found; no files were removed"],
            "manifest_cleaned": False,
        }

    removed_files: list[str] = []
    restored_files: list[str] = []
    skipped_modified: list[str] = []
    not_found: list[str] = []
    errors: list[str] = []
    remaining_files: dict[str, dict[str, str]] = {}

    for relative_path, metadata in manifest_data["files"].items():
        full_path = _safe_join(target_root, relative_path)
        if not full_path.exists() and not full_path.is_symlink():
            not_found.append(relative_path)
            continue
        if full_path.is_symlink():
            errors.append(f"Refused symbolic link: {relative_path}")
            remaining_files[relative_path] = metadata
            continue

        current_hash = compute_file_sha256(full_path)
        modified = current_hash != metadata["sha256"]
        if modified and not (force or clean_modified):
            skipped_modified.append(relative_path)
            remaining_files[relative_path] = metadata
            continue

        backup_relative = metadata.get("backup_path")
        try:
            if not dry_run:
                if backup_relative:
                    backup_path = _safe_join(target_root, backup_relative)
                    if not backup_path.is_file() or backup_path.is_symlink():
                        raise ManifestError(f"Missing or unsafe backup for {relative_path}")
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_path, full_path, follow_symlinks=False)
                    backup_path.unlink()
                    restored_files.append(relative_path)
                    clean_empty_parents(
                        backup_path.parent,
                        target_root / ".agents" / ".ultimate-travel-agent-backups",
                    )
                else:
                    full_path.unlink()
                    removed_files.append(relative_path)
                    clean_empty_parents(full_path.parent, target_root / ".agents")
            elif backup_relative:
                restored_files.append(relative_path)
            else:
                removed_files.append(relative_path)
        except (OSError, ManifestError) as exc:
            errors.append(f"{relative_path}: {exc}")
            remaining_files[relative_path] = metadata

    manifest_path = get_install_manifest_path(target_root)
    if not dry_run:
        if remaining_files:
            manifest_data["files"] = remaining_files
            save_install_manifest(target_root, manifest_data)
        else:
            if manifest_path.exists():
                manifest_path.unlink()
            clean_empty_parents(target_root / ".agents", target_root)

    return {
        "removed": removed_files,
        "restored": restored_files,
        "skipped_modified": skipped_modified,
        "not_found": not_found,
        "errors": errors,
        "manifest_cleaned": not remaining_files and not dry_run,
    }


def sync_pack_mirror(
    check: bool = False, repository_root: Path | None = None
) -> dict[str, list[str]]:
    """Generate or check the compatibility mirror from canonical .agents assets."""

    repo = (repository_root or Path(__file__).resolve().parent.parent.parent).resolve()
    canonical = repo / ".agents"
    mirror = repo / "packages" / "travel-skills"
    manifest = get_manifest(canonical)
    changed: list[str] = []
    out_of_sync: list[str] = []

    files = ["manifest.json"] + [str(entry["path"]) for entry in manifest["skills"]]
    for relative_path in files:
        source = _safe_join(canonical, relative_path)
        destination = _safe_join(mirror, relative_path)
        differs = not destination.exists() or compute_file_sha256(source) != compute_file_sha256(
            destination
        )
        if not differs:
            continue
        if check:
            out_of_sync.append(relative_path)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)
        changed.append(relative_path)
    return {"changed": changed, "out_of_sync": out_of_sync}
