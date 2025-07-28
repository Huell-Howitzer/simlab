Ah — now we’re talking about the real trick: getting the environment updates from a Python subprocess to persist in your local terminal session, just like source ./some_script.sh does in Bash.

Here’s the key point:

⸻

❌ The Problem

A subprocess (like a Python script) can’t change the environment of your shell.

	•	Environment variables are process-local.
	•	A child (Python) process can’t reach back and change the parent shell’s environment.

So even though you can make a Python script figure out what env vars to set, it cannot directly inject them into your shell… unless you go through a clever intermediate step.

⸻

✅ The Solution: Emit Shell Code, Then eval It

To make this work like source, do this:
	1.	Run your Python script to print the desired exports as shell commands (export KEY=value).
	2.	Capture that output in your shell.
	3.	eval it in the current shell, so the variables are set in-place.

This pattern is well-known in tools like direnv, conda, or custom .env loaders.

⸻

🛠️ How to Do It

🐍 1. Python Script: env_bootstrap.py

# env_bootstrap.py
import json

def main():
    env_vars = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DEBUG": "true"
    }

    for key, val in env_vars.items():
        print(f'export {key}="{val}"')

if __name__ == "__main__":
    main()

This prints:

export DB_HOST="localhost"
export DB_PORT="5432"
export DEBUG="true"


⸻

🖥️ 2. Shell Wrapper: sourcepy Function

Add this shell function to your .bashrc / .zshrc:

sourcepy() {
    eval "$($1)"
}

Then reload your shell:

source ~/.bashrc  # or ~/.zshrc


⸻

▶️ 3. Use It Like This:

sourcepy python3 env_bootstrap.py

✅ Now DB_HOST, DB_PORT, and DEBUG will be set in your current terminal session, just like if you sourced a .sh file.

⸻

🔐 Optional: Use Shared Memory Behind the Scenes

If you still want the Python script to:
	•	Pull from secrets
	•	Decrypt files
	•	Load from shared memory, etc.

…do all of that inside the Python script, then just output the final export lines.

⸻

🧠 Summary

Goal	Can we do it?	How?
Persist env vars in current shell from Python	✅ Yes	Print export KEY=VAL → use eval in shell


⸻

🧩 Bonus: Example env_bootstrap.py with Logic

# env_bootstrap.py
import os

def get_region():
    # Simulate logic (e.g., detect cloud region)
    return "us-west-2"

def main():
    values = {
        "API_KEY": "abc123",
        "DEBUG_MODE": "1",
        "REGION": get_region()
    }

    for key, val in values.items():
        print(f'export {key}="{val}"')

if __name__ == "__main__":
    main()

Then use it:

sourcepy python3 env_bootstrap.py
echo $REGION  # us-west-2


⸻

Let me know if you want this turned into a reusable CLI tool (like sourcepy) with .pyenv files or venv detection!