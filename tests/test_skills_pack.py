import os
import shutil
import tempfile
from pathlib import Path
import pytest
from ultimate_travel_agent.cli import install_skills, uninstall_skills
import argparse
import yaml

def get_base_dir():
    return Path(os.path.abspath(__file__)).parent.parent

def test_install_in_temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(
            command="install-skills",
            target=tmpdir,
            include_agents=True,
            include_workflows=True,
            force=False
        )
        install_skills(args)
        
        target_path = Path(tmpdir)
        # Check skills are installed
        assert (target_path / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md").exists()
        # Check workflows are installed
        assert (target_path / ".agents" / "workflows" / "plan-complete-trip.md").exists()
        # Check agents are installed
        assert (target_path / ".agents" / "travel-orchestrator" / "agent.yaml").exists()

def test_no_overwrite_without_force():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(
            command="install-skills",
            target=tmpdir,
            include_agents=False,
            include_workflows=False,
            force=False
        )
        install_skills(args)
        
        # Modify a file
        skill_path = Path(tmpdir) / ".agents" / "skills" / "travel-orchestrator" / "SKILL.md"
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write("MODIFIED")
            
        # Reinstall without force
        install_skills(args)
        with open(skill_path, "r", encoding="utf-8") as f:
            assert f.read() == "MODIFIED"
            
        # Reinstall with force
        args.force = True
        install_skills(args)
        with open(skill_path, "r", encoding="utf-8") as f:
            assert f.read() != "MODIFIED"

def test_uninstall():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(
            command="install-skills",
            target=tmpdir,
            include_agents=False,
            include_workflows=False,
            force=False
        )
        install_skills(args)
        
        assert (Path(tmpdir) / ".agents" / "skills").exists()
        
        un_args = argparse.Namespace(
            command="uninstall-skills",
            target=tmpdir
        )
        uninstall_skills(un_args)
        
        assert not (Path(tmpdir) / ".agents" / "skills").exists()

def test_skill_frontmatter_and_policies():
    skills_dir = get_base_dir() / "packages" / "travel-skills" / "skills"
    
    for skill_folder in skills_dir.iterdir():
        if skill_folder.is_dir():
            skill_md = skill_folder / "SKILL.md"
            assert skill_md.exists()
            content = skill_md.read_text(encoding="utf-8")
            
            # YAML frontmatter
            assert content.startswith("---")
            frontmatter_end = content.find("---", 3)
            assert frontmatter_end != -1
            
            # Check safety policies
            assert "Never make purchases" in content or "Safety Policy:" in content
            
            # Check fallback / no web search behavior
            assert "live research cannot be completed" in content or "Use only user-provided or local information" in content
            
def test_brief_examples_exist():
    examples_dir = get_base_dir() / "examples"
    assert (examples_dir / "trip-brief-template.md").exists()
    assert (examples_dir / "city-break-brief.md").exists()
    assert (examples_dir / "road-trip-brief.md").exists()
    assert (examples_dir / "nature-low-crowd-brief.md").exists()

def test_no_mcp_api_components_in_main():
    base_dir = get_base_dir()
    src_dir = base_dir / "src" / "ultimate_travel_agent"
    
    # These should be removed in the pivot
    assert not (src_dir / "mcp").exists()
    assert not (src_dir / "integrations").exists()
    assert not (src_dir / "web").exists()
    assert not (base_dir / "docker-compose.yml").exists()

def test_no_secrets_and_personal_paths():
    base_dir = get_base_dir()
    
    for root, dirs, files in os.walk(base_dir):
        if ".git" in root or "node_modules" in root or "__pycache__" in root:
            continue
        for file in files:
            if not file.endswith((".py", ".md", ".json", ".yaml", ".yml")):
                continue
            path = Path(root) / file
            try:
                content = path.read_text(encoding="utf-8")
                assert "c:\\Users\\eliot" not in content, f"Found personal path in {path}"
                assert "API_KEY" not in content or "mock" in content.lower() or "example" in content.lower(), f"Found potential API key in {path}"
            except UnicodeDecodeError:
                pass
