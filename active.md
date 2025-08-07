Perfect — you’re on Linux and do not want to require admin privileges.

Here’s a way to detect if the current user (the one running the script) is:
	•	In a graphical session
	•	And actively using the computer (not idle)

This approach:
	•	Works without root
	•	Works on X11
	•	Limited support on Wayland (due to permission isolation)

⸻

✅ Plan (No Admin Required)

Since you’re not root, you can only reliably check your own session. Here’s what you can do:

🔹 1. Check if you’re in a graphical session

Environment variables like $DISPLAY or $XDG_SESSION_TYPE can tell you.

import os

def in_graphical_session():
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


⸻

🔹 2. Check if you’re idle (on X11) using xprintidle

This tells you how many milliseconds since your last input.

sudo apt install xprintidle

Python wrapper:

import subprocess

def get_idle_time_ms():
    try:
        result = subprocess.run(['xprintidle'], capture_output=True, text=True)
        return int(result.stdout.strip())
    except Exception:
        return None

You can then define a threshold like 5 minutes (300,000 ms):

def is_user_active(idle_threshold_ms=300_000):
    idle_time = get_idle_time_ms()
    return idle_time is not None and idle_time < idle_threshold_ms


⸻

🧪 Full Example Script (X11 Only, No Root)

import os
import subprocess

def in_graphical_session():
    return bool(os.environ.get("DISPLAY"))

def get_idle_time_ms():
    try:
        result = subprocess.run(['xprintidle'], capture_output=True, text=True)
        return int(result.stdout.strip())
    except Exception:
        return None

def is_user_active(idle_threshold_ms=300_000):
    if not in_graphical_session():
        return False
    idle = get_idle_time_ms()
    if idle is None:
        return False
    return idle < idle_threshold_ms

if __name__ == "__main__":
    if is_user_active():
        print("User is actively using the computer.")
    else:
        print("User is idle or not in a graphical session.")


⸻

🧱 Wayland?

Unfortunately, Wayland restricts access to idle/input events for security. Unless you’re using something like GNOME’s D-Bus APIs (and even then only for the current user), it’s tough to get idle time without privileged access.

If you’re on Wayland and using GNOME, you can try:

gdbus call --session --dest org.gnome.Mutter.IdleMonitor \
  --object-path /org/gnome/Mutter/IdleMonitor/Core \
  --method org.gnome.Mutter.IdleMonitor.GetIdletime

But this only works in some setups and may still fail due to sandboxing.

⸻

✅ Summary

Task	Solution
Detect graphical session	Check $DISPLAY or $WAYLAND_DISPLAY
Detect idle time (X11)	Use xprintidle (no root needed)
Detect activity	If idle time < 5 mins, assume active
Wayland support	Very limited without elevated privileges


⸻

Let me know if you’re on Wayland and I can try to help within those limits, or if you want a version that checks all users (which would require elevated permissions).