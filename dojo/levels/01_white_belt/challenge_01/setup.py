import os
from pathlib import Path
import subprocess

def main():
    project_dir = Path(__file__).parent / "project"
    if project_dir.exists():
        os.rmdir(project_dir)
    project_dir.mkdir()