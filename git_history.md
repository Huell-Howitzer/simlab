```python
#!/usr/bin/env python3

import subprocess
import sys

def search_git_commit_messages(search_string):
    try:
        # Run `git log` to get SHA + full message body
        result = subprocess.run(
            ["git", "log", "--format=%H%n%B"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e.stderr}")
        sys.exit(1)

    # Split by commit SHA
    commits = result.stdout.strip().split("\n\ncommit ")

    for block in result.stdout.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if not lines:
            continue

        sha = lines[0]
        message = "\n".join(lines[1:]).strip()

        if search_string in message:
            print(f"\n--- Found in commit {sha} ---")
            print(f"Message:\n{message}")
            print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_git_history.py <search_string>")
        sys.exit(1)

    search_term = sys.argv[1]
    search_git_commit_messages(search_term)
```