import os
import subprocess
from pathlib import Path

def main():
    project_dir = Path(__file__).parent / "project"
    if not project_dir.exists():
        print("❌ Project directory not found")
        return

    os.chdir(project_dir)
    result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
    commits = result.stdout.strip().splitlines()

    if len(commits) < 2:
        print("❌ No new commit found. Try adding a commit.")
    else:
        print("🥋 Great job! You made a commit.")
