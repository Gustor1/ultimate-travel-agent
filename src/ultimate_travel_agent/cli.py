import argparse
import os
import shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--target")
    parser.add_argument("--include-agents", action="store_true")
    parser.add_argument("--include-workflows", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    
    if args.command == "install-skills" and args.target:
        os.makedirs(os.path.join(args.target, ".agents", "skills"), exist_ok=True)
        print("Installed skills")
