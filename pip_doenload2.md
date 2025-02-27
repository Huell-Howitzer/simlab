Below is an example Python script that takes a package name as an argument, fetches its metadata from PyPI’s JSON API, and then recursively finds its dependencies. This script uses the packaging library to parse dependency strings. (If you don’t have it installed, you can install it via pip install packaging.)

#!/usr/bin/env python3
import requests
import sys
from packaging.requirements import Requirement

def get_package_info(package):
    """
    Fetch package info from PyPI.
    """
    url = f"https://pypi.org/pypi/{package}/json"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Package '{package}' not found on PyPI.")
        return None
    return response.json()

def parse_dependency(dep_str):
    """
    Parse a dependency string using packaging's Requirement.
    Returns the dependency name.
    """
    try:
        req = Requirement(dep_str)
        return req.name
    except Exception:
        # Fallback: use the first word from the string.
        return dep_str.split()[0]

def get_dependencies(package, seen=None):
    """
    Recursively retrieve dependencies for the given package.
    'seen' keeps track of packages already processed.
    Returns a dict mapping package names to their dependencies.
    """
    if seen is None:
        seen = set()

    if package in seen:
        return {}
    seen.add(package)

    info = get_package_info(package)
    if info is None:
        return {}

    requires = info.get("info", {}).get("requires_dist")
    deps = {}
    if requires:
        for dep_str in requires:
            # Sometimes a dependency may include an environment marker.
            # For simplicity, this script does not evaluate markers.
            dep_name = parse_dependency(dep_str)
            # Recursively get sub-dependencies
            deps[dep_name] = get_dependencies(dep_name, seen)
    return deps

def print_dependencies(deps, level=0):
    """
    Print the dependency tree with indentation based on level.
    """
    indent = "  " * level
    for package, subdeps in deps.items():
        print(f"{indent}- {package}")
        print_dependencies(subdeps, level + 1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <package_name>")
        sys.exit(1)

    package_name = sys.argv[1]
    print(f"Fetching dependencies for '{package_name}'...\n")
    dependency_tree = {package_name: get_dependencies(package_name)}
    print_dependencies(dependency_tree)

if __name__ == "__main__":
    main()

How It Works
	1.	Fetching Package Data:
The function get_package_info retrieves the JSON metadata for a package from PyPI.
	2.	Parsing Dependencies:
The dependency strings (from the requires_dist field) are parsed using the Requirement class from the packaging library. This extracts just the package name (ignoring version specifiers and markers).
	3.	Recursion and Avoiding Cycles:
The get_dependencies function recursively processes each dependency. A set named seen prevents infinite loops if there are circular dependencies.
	4.	Output:
The print_dependencies function displays the dependency tree with indentation reflecting the recursion depth.

Run the script from the command line like so:

python script.py requests

This will print out the dependency tree for the requests package (or whichever package you choose).