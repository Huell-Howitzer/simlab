Perfect. Since make already outputs progress-like logs, we can hook into its output to drive the animation. Here’s how to proceed:

⸻

Approach
	1.	Start the plane at the left.
	2.	Run make as a subprocess, capturing output.
	3.	Estimate progress based on:
	•	Number of lines matched (make prints targets or commands).
	•	Optional: parse make -n beforehand to estimate total steps.
	4.	Update the plane’s position accordingly.
	5.	When make finishes, plane lands at far right.

⸻

Working Python Skeleton

import math
import shutil
import subprocess
import time
from rich.console import Console
from rich.live import Live

console = Console()
term_width, term_height = shutil.get_terminal_size()

def generate_frame(x, y):
    lines = [' ' * term_width for _ in range(term_height)]
    row = list(lines[y])
    row[x] = '✈️'
    lines[y] = ''.join(row)
    return '\n'.join(lines)

def get_position(progress_ratio):
    x = int(progress_ratio * (term_width - 2)) + 1
    y = int((1 - math.sin(progress_ratio * math.pi)) * ((term_height - 4) / 2)) + 1
    return x, y

def estimate_make_steps():
    try:
        result = subprocess.run(["make", "-n"], capture_output=True, text=True, check=True)
        # Count command-like lines (naive way)
        return sum(1 for line in result.stdout.splitlines() if line.strip() and not line.startswith("make"))
    except subprocess.CalledProcessError:
        return 20  # fallback

def run_make_and_animate():
    total_steps = estimate_make_steps()
    completed = 0

    with Live("", console=console, refresh_per_second=30) as live:
        process = subprocess.Popen(
            ["make"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in process.stdout:
            console.print(line.rstrip())
            completed += 1
            ratio = min(completed / total_steps, 1.0)
            x, y = get_position(ratio)
            live.update(generate_frame(x, y))

        process.wait()
        if process.returncode == 0:
            console.print("[green]Make finished. Plane has landed!")
        else:
            console.print("[red]Build failed.")

def main():
    console.print("[bold cyan]Starting build animation for Make...[/]")
    run_make_and_animate()

if __name__ == "__main__":
    main()


⸻

Benefits
	•	Live airplane animation synced to real build progress.
	•	Handles noisy output gracefully.
	•	Easily extendable for pre-make steps (e.g., untar files, etc.).

⸻

Optional Improvements
	•	Show step names as subtitles.
	•	Add a “landing” effect (bounce or slow stop).
	•	Handle make errors with an explosion emoji, if you’re into drama.

Would you like me to include those pre-make steps (tar.gz, copying) into this same framework too?