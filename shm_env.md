That’s a great insight — and you’re absolutely right: this is a perfect use case for a callback-based (or context-style) function, where:
	•	The setup (shared memory creation and subprocess launch) is fixed,
	•	The teardown (read, apply, and cleanup) is also fixed,
	•	The “middle” logic — the environment-producing behavior — is what varies (your callback).

This leads to a clean, reusable pattern that’s both flexible and extensible.

⸻

✅ Let’s Refactor Using a Callback

We’ll turn the parent into a generic utility that:
	1.	Creates shared memory
	2.	Runs a callback (which could be subprocess.run(...), or anything else)
	3.	Reads the environment vars from shared memory
	4.	Applies them to os.environ

⸻

🧱 env_loader.py (Refactored)

# env_loader.py
import os
import json
from multiprocessing import shared_memory

def load_env_from_shared_memory(callback, shm_name="env_shm", shm_size=2048):
    # Step 1: Create shared memory
    shm = shared_memory.SharedMemory(create=True, size=shm_size, name=shm_name)
    shm.buf[:shm_size] = bytes(shm_size)  # zero it

    try:
        # Step 2: Run user-defined logic
        callback(shm_name)

        # Step 3: Read and decode environment vars
        data = bytes(shm.buf[:shm_size]).rstrip(b'\x00')
        if not data:
            print("[env_loader] No data received.")
            return {}

        env_vars = json.loads(data.decode())
        print(f"[env_loader] Received env vars: {env_vars}")

        # Step 4: Apply to os.environ
        for k, v in env_vars.items():
            os.environ[k] = v
            print(f"[env_loader] Applied {k} = {v}")

        return env_vars

    finally:
        shm.close()
        shm.unlink()


⸻

🧪 Sample Use Case

Let’s use this from a main.py to run your env_setter.py subprocess:

# main.py
import subprocess
from env_loader import load_env_from_shared_memory

def run_env_subprocess(shm_name):
    subprocess.run(["python3", "env_setter.py", shm_name], check=True)

def main():
    print("Before:")
    print("DEBUG =", os.environ.get("DEBUG"))

    load_env_from_shared_memory(run_env_subprocess)

    print("\nAfter:")
    print("DEBUG =", os.environ.get("DEBUG"))
    print("API_KEY =", os.environ.get("API_KEY"))

if __name__ == "__main__":
    main()


⸻

🧩 env_setter.py (Same as Before)

No change needed here unless you want to modularize further:

# env_setter.py
import sys
import json
from multiprocessing import shared_memory

def get_env_vars():
    return {
        "API_KEY": "abc123",
        "DEBUG": "true",
        "REGION": "us-west-1"
    }

def main():
    shm_name = sys.argv[1]
    shm = shared_memory.SharedMemory(name=shm_name)

    env_vars = get_env_vars()
    encoded = json.dumps(env_vars).encode()
    shm.buf[:len(encoded)] = encoded
    shm.close()

if __name__ == "__main__":
    main()


⸻

🧠 Benefits of the Callback Pattern
	•	Extensible: You can swap in a subprocess, a Python function, a remote API call, etc.
	•	Testable: You can mock the callback during testing.
	•	Clean lifecycle: Setup → Do work → Teardown, all in one place.
	•	Composable: Can be wrapped in context managers or decorators.

⸻

🛠️ Want It Cleaner?

We can further upgrade to a context manager (with with syntax) or make the callback async-safe.

Would you like to turn this into a class-based or @contextmanager-based version?