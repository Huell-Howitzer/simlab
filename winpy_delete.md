You’re running into a common problem on Windows where shutil.rmtree() fails due to:
	•	Files being in use or open (especially by other processes)
	•	Read-only file attributes
	•	Antivirus or indexing services locking files
	•	Symbolic links, junctions, or special file permissions

To force deletion reliably on Windows, here are several strategies you can apply:

⸻

✅ 1. Use shutil.rmtree with an error handler

This allows you to forcibly remove read-only files:

import os
import shutil
import stat

def force_remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

shutil.rmtree('your_dir', onerror=force_remove_readonly)


⸻

✅ 2. Use pathlib + file closing best practices

Make absolutely sure you’re not leaking open file handles:

from pathlib import Path

with open('some_file.txt', 'w') as f:
    f.write("data")
# f is now properly closed

# Now safe to delete the directory
shutil.rmtree(Path('your_dir'), onerror=force_remove_readonly)


⸻

✅ 3. Kill locking processes (advanced but dangerous)

You can use psutil to find and kill processes locking files—but use with extreme caution:

import psutil

def kill_processes_using(path):
    for proc in psutil.process_iter(['pid', 'open_files']):
        try:
            for file in proc.info['open_files'] or []:
                if path in file.path:
                    proc.kill()
        except Exception:
            pass


⸻

✅ 4. Use Windows-native deletion via subprocess

Windows’ rd /s /q is aggressive and bypasses some of Python’s permission issues:

import subprocess

def windows_delete_force(path):
    subprocess.run(['cmd', '/c', 'rd', '/s', '/q', path], shell=True)


⸻

✅ 5. Final all-in-one solution

Here’s a utility that combines all of the above, checks platform, and ensures deletion:

import os
import shutil
import stat
import subprocess
import sys

def on_rm_error(func, path, _):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Error force-deleting {path}: {e}")

def force_delete(path):
    if os.name == 'nt':
        # Try native Windows deletion first
        subprocess.run(['cmd', '/c', 'rd', '/s', '/q', path], shell=True)
        if os.path.exists(path):
            shutil.rmtree(path, onerror=on_rm_error)
    else:
        shutil.rmtree(path, onerror=on_rm_error)

# Example usage
force_delete('your_dir')


⸻

🧪 Debug Tips:
	•	Use handle.exe from Sysinternals to find file locks: handle your_dir
	•	Always close file handles (f.close() or use with)
	•	Disable antivirus temporarily for test cases (just to confirm if it’s interfering)

⸻

Let me know if you’re still seeing specific errors (especially PermissionError, FileNotFoundError, etc.)—we can fine-tune based on those.