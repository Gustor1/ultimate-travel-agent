import argparse
import os
import shutil
import sys
from pathlib import Path

def get_base_dir():
    # In this project, packages/travel-skills and .agents are in the repo root
    # If installed as a package, we'd find them differently, but for now repo root:
    return Path(os.path.abspath(__file__)).parent.parent.parent

def copy_directory(src_dir, dest_dir, force, installed_files):
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    if not src_path.exists():
        return
        
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for item in src_path.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(src_path)
            target_file = dest_path / rel_path
            
            if target_file.exists() and not force:
                print(f"Skipping {target_file} (already exists, use --force to overwrite)")
                continue
                
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
            installed_files.append(target_file)
            print(f"Installed: {target_file}")

def install_skills(args):
    target = Path(args.target)
    base_dir = get_base_dir()
    
    installed_files = []
    
    # 1. Install skills
    skills_src = base_dir / "packages" / "travel-skills" / "skills"
    if not skills_src.exists():
        # Fallback to .agents/skills if packages one doesn't exist
        skills_src = base_dir / ".agents" / "skills"
        
    skills_dest = target / ".agents" / "skills"
    copy_directory(skills_src, skills_dest, args.force, installed_files)
    
    # 2. Install agents
    if args.include_agents:
        agents_src = base_dir / ".agents"
        # We need to copy agents, but not skills and workflows which are in subdirs
        if agents_src.exists():
            for item in agents_src.iterdir():
                if item.is_dir() and item.name not in ["skills", "workflows"]:
                    copy_directory(item, target / ".agents" / item.name, args.force, installed_files)

    # 3. Install workflows
    if args.include_workflows:
        workflows_src = base_dir / ".agents" / "workflows"
        workflows_dest = target / ".agents" / "workflows"
        copy_directory(workflows_src, workflows_dest, args.force, installed_files)
        
    print(f"\nSummary: {len(installed_files)} files installed successfully.")
    
def uninstall_skills(args):
    target = Path(args.target)
    
    uninstalled_count = 0
    # Uninstall skills
    skills_dest = target / ".agents" / "skills"
    if skills_dest.exists():
        shutil.rmtree(skills_dest)
        uninstalled_count += 1
        print(f"Removed: {skills_dest}")
        
    # We could theoretically remove agents and workflows too if we track them, 
    # but the simplest safe uninstall is to remove the skills directory and specific agents
    print(f"\nSummary: Uninstalled travel skills from {target}")

def main():
    parser = argparse.ArgumentParser(description="Ultimate Travel Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    install_parser = subparsers.add_parser("install-skills")
    install_parser.add_argument("--target", required=True, help="Target project path")
    install_parser.add_argument("--include-agents", action="store_true", help="Include sub-agents")
    install_parser.add_argument("--include-workflows", action="store_true", help="Include workflows")
    install_parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    uninstall_parser = subparsers.add_parser("uninstall-skills")
    uninstall_parser.add_argument("--target", required=True, help="Target project path")
    
    args = parser.parse_args()
    
    if args.command == "install-skills":
        install_skills(args)
    elif args.command == "uninstall-skills":
        uninstall_skills(args)

if __name__ == "__main__":
    main()
