"""Stable, provider-neutral measurements for prompt asset regression budgets."""

from pathlib import Path


def _measure(files: list[Path]) -> dict[str, int]:
    lengths = [len(path.read_text(encoding="utf-8")) for path in files]
    characters = sum(lengths)
    return {
        "files": len(files),
        "characters": characters,
        "estimated_tokens": (characters + 3) // 4,
        "largest_file_characters": max(lengths, default=0),
    }


def audit_prompt_corpus(agents_root: Path) -> dict[str, dict[str, int]]:
    """Measure canonical prompt entrypoints and shared Markdown instructions.

    The token estimate is intentionally a transparent four-characters-per-token
    proxy.  It supports repository comparisons; it is not provider billing data.
    """

    root = agents_root.resolve()
    groups = {
        "skills": sorted((root / "skills").glob("*/SKILL.md")),
        "agents": sorted((root / "agents").glob("*/agent.md")),
        "workflows": sorted((root / "workflows").glob("*.md")),
        "shared": sorted((root / "shared").glob("*.md")),
    }
    return {name: _measure(files) for name, files in groups.items()}
