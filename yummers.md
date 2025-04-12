import subprocess

# List of packages you want to check
packages = [
    "vim",
    "htop",
    "gcc",
    "nonexistent-package",
    # add more here...
]

def get_available_packages():
    try:
        result = subprocess.run(
            ["yum", "list", "available"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        available_lines = result.stdout.splitlines()
        available_pkgs = set()

        for line in available_lines:
            # Skip headers and parse valid lines
            if line and not line.startswith("Loaded plugins") and not line.startswith("Available Packages"):
                parts = line.split()
                if parts:
                    available_pkgs.add(parts[0].split('.')[0])  # Remove arch suffix if present

        return available_pkgs

    except Exception as e:
        print(f"Error running yum list available: {e}")
        return set()

if __name__ == "__main__":
    available = get_available_packages()

    for pkg in packages:
        status = "AVAILABLE" if pkg in available else "NOT AVAILABLE"
        print(f"{pkg}: {status}")