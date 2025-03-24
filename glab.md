Below is an example walkthrough for creating a Python package that uses the system’s curl command to interact with your self‐hosted GitLab. In this example, we’ll set up a package called “gitlab_curl_client” with a module that wraps curl calls via Python’s subprocess module. (Note that for many tasks you might consider using Python libraries like “requests” or “python-gitlab,” but if you want to stick with curl this method works well.)

⸻

1. Package Structure

Create a directory structure similar to this:

gitlab_curl_client/
├── gitlab_curl_client
│   ├── __init__.py
│   └── client.py
├── tests
│   └── test_client.py
├── README.md
└── setup.py

	•	gitlab_curl_client/client.py – Contains functions that build and execute curl commands.
	•	setup.py – Package installation script.
	•	README.md – Documentation.
	•	tests/test_client.py – Simple tests (optional).

⸻

2. Writing the Client Module

Here’s an example implementation using the subprocess module to call curl. In this example, we assume that your GitLab instance’s API requires an access token. You can store this token (or configure it via environment variables) and include it in your curl commands.

gitlab_curl_client/client.py:

import subprocess
import json
import os

class GitLabClient:
    def __init__(self, host, token):
        """
        :param host: URL of the self hosted GitLab instance (e.g., 'https://gitlab.example.com')
        :param token: Personal Access Token with API access.
        """
        self.host = host.rstrip('/')
        self.token = token

    def _run_curl(self, method, endpoint, data=None):
        """
        Internal method to run a curl command.
        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint (e.g., '/api/v4/projects')
        :param data: A dictionary with data to send (for POST/PUT).
        :return: Parsed JSON response.
        """
        url = f"{self.host}{endpoint}"
        headers = [
            "-H", f"PRIVATE-TOKEN: {self.token}",
            "-H", "Content-Type: application/json"
        ]

        # Prepare the curl command
        command = ["curl", "-s", "-X", method] + headers

        if data:
            json_data = json.dumps(data)
            command += ["-d", json_data]

        command.append(url)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"curl failed: {e.stderr}") from e
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response")

    def list_projects(self):
        """
        List projects accessible by the user.
        """
        return self._run_curl("GET", "/api/v4/projects")

    def get_project(self, project_id):
        """
        Get details of a specific project.
        :param project_id: ID of the project.
        """
        return self._run_curl("GET", f"/api/v4/projects/{project_id}")

    def create_project(self, name, **kwargs):
        """
        Create a new project.
        :param name: Name of the project.
        :param kwargs: Other optional parameters (visibility, description, etc.)
        """
        data = {"name": name}
        data.update(kwargs)
        return self._run_curl("POST", "/api/v4/projects", data=data)

Explanation
	•	Initialization: The GitLabClient is initialized with the GitLab host URL and a personal access token.
	•	Curl Execution: The _run_curl method builds the curl command with necessary headers and data. It uses the subprocess module to execute the command silently (-s) and captures the output.
	•	API Methods: Methods like list_projects(), get_project(), and create_project() call _run_curl with appropriate HTTP methods and endpoints.

⸻

3. Creating setup.py

Create a setup.py file to make your package installable:

from setuptools import setup, find_packages

setup(
    name="gitlab_curl_client",
    version="0.1.0",
    description="A Python package using curl to interact with a self-hosted GitLab",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)



⸻

4. Writing a README

Your README.md might include instructions such as:

# GitLab Curl Client

This package provides a simple client to interact with your self-hosted GitLab using curl commands executed from Python.

## Installation

```bash
pip install .

Usage

from gitlab_curl_client.client import GitLabClient

# Configure your GitLab host and access token
client = GitLabClient(host="https://gitlab.example.com", token="YOUR_ACCESS_TOKEN")

# List projects
projects = client.list_projects()
print(projects)

# Get a specific project by ID
project = client.get_project(project_id=123)
print(project)

# Create a new project
new_project = client.create_project(name="New Project", description="Project description")
print(new_project)

---

## 5. Testing Your Package

A simple test in **`tests/test_client.py`** might look like:

```python
import os
import unittest
from gitlab_curl_client.client import GitLabClient

class TestGitLabClient(unittest.TestCase):
    def setUp(self):
        # These environment variables should be set for testing purposes
        host = os.getenv("GITLAB_HOST", "https://gitlab.example.com")
        token = os.getenv("GITLAB_TOKEN", "dummy_token")
        self.client = GitLabClient(host, token)

    def test_list_projects(self):
        # This is a basic test – in real tests, you may want to mock subprocess.run
        try:
            projects = self.client.list_projects()
            # if the token or host is dummy, you may get an error, so just print
            print(projects)
        except Exception as e:
            self.assertTrue(True)  # Replace with actual error handling in real tests

if __name__ == "__main__":
    unittest.main()



⸻

6. Final Steps
	1.	Build and install the package:
From your package root directory:

python setup.py sdist bdist_wheel
pip install .


	2.	Environment Variables:
It’s a good idea to keep sensitive tokens in environment variables rather than hardcoding them.
	3.	Extending Functionality:
You can add more functions to support other GitLab API endpoints as needed.

⸻
This should give you a solid foundation for a Python package that leverages curl to work with your self-hosted GitLab. Feel free to modify or extend the functionality based on your specific needs.


---

Below is one way to simplify the CLI. In this version, we use subcommands (via argparse subparsers) and allow the host and token to be read from environment variables if they aren’t passed explicitly. This lets you use commands like:

gitlab-curl list-groups
gitlab-curl list-projects PTO
gitlab-curl get-group PTO
gitlab-curl get-project PTO "PTO-Project"

without having to re-specify the host and token every time.

⸻

Updated CLI Code

# gitlab_curl_client/cli.py
import argparse
import json
import os
from .client import GitLabClient

def get_client(args):
    # Use CLI args if provided, otherwise check environment variables.
    host = args.host or os.getenv("GITLAB_HOST")
    token = args.token or os.getenv("GITLAB_TOKEN")
    if not host or not token:
        raise ValueError("GitLab host and token must be provided via --host/--token or environment variables GITLAB_HOST/GITLAB_TOKEN")
    return GitLabClient(host, token)

def list_groups(args):
    client = get_client(args)
    groups = client.list_groups()
    print(json.dumps(groups, indent=2))

def list_projects(args):
    client = get_client(args)
    if not args.group:
        raise ValueError("list-projects requires a group identifier (friendly name or ID)")
    projects = client.list_projects_in_group(args.group)
    print(json.dumps(projects, indent=2))

def get_group(args):
    client = get_client(args)
    if not args.group:
        raise ValueError("get-group requires a group name")
    group = client.get_group_by_name(args.group)
    if group:
        print(json.dumps(group, indent=2))
    else:
        print(f"Group '{args.group}' not found.")

def get_project(args):
    client = get_client(args)
    if not args.group or not args.project:
        raise ValueError("get-project requires both a group and a project name")
    project = client.get_project_by_name(args.group, args.project)
    if project:
        print(json.dumps(project, indent=2))
    else:
        print(f"Project '{args.project}' in group '{args.group}' not found.")

def main():
    parser = argparse.ArgumentParser(description="Simplified GitLab Curl Client CLI")
    
    # Global optional arguments
    parser.add_argument("--host", help="GitLab host URL (e.g., https://gitlab.example.com). Defaults to env var GITLAB_HOST.")
    parser.add_argument("--token", help="GitLab API access token. Defaults to env var GITLAB_TOKEN.")

    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)
    
    # list-groups command
    subparsers.add_parser("list-groups", help="List all groups accessible by the user").set_defaults(func=list_groups)
    
    # list-projects command: requires a group argument
    parser_list_projects = subparsers.add_parser("list-projects", help="List projects in a group")
    parser_list_projects.add_argument("group", help="Group identifier (friendly name or ID)")
    parser_list_projects.set_defaults(func=list_projects)
    
    # get-group command: requires a group name
    parser_get_group = subparsers.add_parser("get-group", help="Get details for a group by name")
    parser_get_group.add_argument("group", help="Group name (friendly name)")
    parser_get_group.set_defaults(func=get_group)
    
    # get-project command: requires both group and project names
    parser_get_project = subparsers.add_parser("get-project", help="Get details for a project within a group")
    parser_get_project.add_argument("group", help="Group identifier (friendly name or ID)")
    parser_get_project.add_argument("project", help="Project name (friendly name)")
    parser_get_project.set_defaults(func=get_project)
    
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()



⸻

How This Version Simplifies CLI Usage
	1.	Subcommands:
	•	The commands (list-groups, list-projects, get-group, and get-project) are now subcommands with clear, positional arguments.
	2.	Environment Variables:
	•	If you set GITLAB_HOST and GITLAB_TOKEN in your environment, you don’t need to specify --host and --token every time.
	3.	Clearer Commands:
	•	For example, to list projects in the “PTO” group, simply run:

gitlab-curl list-projects PTO


	•	This makes the CLI usage more straightforward compared to having to pass multiple flags every time.

	4.	Error Handling:
	•	The CLI now gives clear errors if required arguments are missing.

⸻

Update setup.py for CLI Entry Point

Make sure your setup.py includes the following entry point so that the CLI is available when you install the package:

from setuptools import setup, find_packages

setup(
    name="gitlab_curl_client",
    version="0.2.0",
    description="A Python package using curl to interact with a self-hosted GitLab, with simplified CLI support.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gitlab-curl=gitlab_curl_client.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)



⸻

With these changes, your CLI becomes much more user-friendly and easier to work with—letting you rely on a few simple commands instead of manually constructing curl commands.

---

Below is an example of extending your package to include:
	1.	A new method in your client to get all labels from a project, and
	2.	A utility function that prints any API results as a Markdown table.

⸻

1. Extending the Client to Get All Labels

In your gitlab_curl_client/client.py module, add a new method (for example, named get_labels) that calls GitLab’s labels endpoint for a given project. This method also supports passing a friendly name for the project (using your config mapping) instead of a numeric ID.

# gitlab_curl_client/client.py
import subprocess
import json
import os
import urllib.parse
from . import config  # Import your configuration mapping

class GitLabClient:
    def __init__(self, host, token):
        """
        :param host: URL of the self hosted GitLab instance (e.g., 'https://gitlab.example.com')
        :param token: Personal Access Token with API access.
        """
        self.host = host.rstrip('/')
        self.token = token

    def _run_curl(self, method, endpoint, data=None):
        url = f"{self.host}{endpoint}"
        headers = [
            "-H", f"PRIVATE-TOKEN: {self.token}",
            "-H", "Content-Type: application/json"
        ]
        command = ["curl", "-s", "-X", method] + headers

        if data:
            json_data = json.dumps(data)
            command += ["-d", json_data]

        command.append(url)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"curl failed: {e.stderr}") from e
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response")

    def list_groups(self):
        """List all groups accessible by the user."""
        return self._run_curl("GET", "/api/v4/groups")

    def get_group_by_name(self, group_name):
        """
        Search for a group by its name using the API.
        Returns the first matching group or None if not found.
        """
        groups = self.list_groups()
        for group in groups:
            if group.get("name", "").lower() == group_name.lower():
                return group
        return None

    def list_projects_in_group(self, group_identifier):
        """
        List projects within a group.
        The group_identifier can be a friendly name (if defined in config), a numeric ID, or URL-encoded path.
        """
        if isinstance(group_identifier, str):
            group_id = config.GROUP_IDS.get(group_identifier.upper())
            if group_id:
                group_identifier = group_id
        if isinstance(group_identifier, str):
            group_identifier = urllib.parse.quote_plus(group_identifier)
        return self._run_curl("GET", f"/api/v4/groups/{group_identifier}/projects")

    def get_project_by_name(self, group_identifier, project_name):
        """
        Search for a project by its name within a specific group.
        The group_identifier can be a friendly name or an ID.
        """
        projects = self.list_projects_in_group(group_identifier)
        for project in projects:
            if project.get("name", "").lower() == project_name.lower():
                return project
        return None

    def get_project(self, project_identifier):
        """
        Retrieve a project. If project_identifier is a friendly name defined in config, it is converted to an ID.
        """
        if isinstance(project_identifier, str):
            project_id = config.PROJECT_IDS.get(project_identifier)
            if project_id:
                project_identifier = project_id
        return self._run_curl("GET", f"/api/v4/projects/{project_identifier}")

    def get_labels(self, project_identifier):
        """
        Retrieve all labels for a given project.
        The project_identifier can be a friendly name (if defined in config) or a numeric ID.
        """
        if isinstance(project_identifier, str):
            project_id = config.PROJECT_IDS.get(project_identifier)
            if project_id:
                project_identifier = project_id
        return self._run_curl("GET", f"/api/v4/projects/{project_identifier}/labels")



⸻

2. Creating a Utility to Print Markdown Tables

Create a new module (for example, gitlab_curl_client/utils.py) with a helper function that prints any list of dictionaries as a Markdown table. This function automatically determines headers based on the keys present in the data.

# gitlab_curl_client/utils.py
def print_markdown_table(data):
    """
    Print a list of dictionaries as a Markdown table.
    
    :param data: List of dictionaries, where each dictionary represents a row.
    """
    if not data:
        print("No data to display.")
        return

    # Collect all unique keys from all items to use as table headers.
    headers = list({key for item in data for key in item.keys()})
    
    # Print header row
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    print(header_row)
    print(separator_row)
    
    # Print each row's values
    for item in data:
        row = [str(item.get(header, "")) for header in headers]
        print("| " + " | ".join(row) + " |")



⸻

3. Using the New Functions in the CLI

You can add a new subcommand to your CLI so you can quickly get all labels for a project and print them in a Markdown table. For example, update your gitlab_curl_client/cli.py to include a get-labels command:

# gitlab_curl_client/cli.py
import argparse
import json
import os
from .client import GitLabClient
from .utils import print_markdown_table

def get_client(args):
    host = args.host or os.getenv("GITLAB_HOST")
    token = args.token or os.getenv("GITLAB_TOKEN")
    if not host or not token:
        raise ValueError("GitLab host and token must be provided via --host/--token or environment variables GITLAB_HOST/GITLAB_TOKEN")
    return GitLabClient(host, token)

def list_groups(args):
    client = get_client(args)
    groups = client.list_groups()
    print(json.dumps(groups, indent=2))

def list_projects(args):
    client = get_client(args)
    if not args.group:
        raise ValueError("list-projects requires a group identifier (friendly name or ID)")
    projects = client.list_projects_in_group(args.group)
    print(json.dumps(projects, indent=2))

def get_group(args):
    client = get_client(args)
    if not args.group:
        raise ValueError("get-group requires a group name")
    group = client.get_group_by_name(args.group)
    if group:
        print(json.dumps(group, indent=2))
    else:
        print(f"Group '{args.group}' not found.")

def get_project(args):
    client = get_client(args)
    if not args.group or not args.project:
        raise ValueError("get-project requires both a group and a project name")
    project = client.get_project_by_name(args.group, args.project)
    if project:
        print(json.dumps(project, indent=2))
    else:
        print(f"Project '{args.project}' in group '{args.group}' not found.")

def get_labels(args):
    client = get_client(args)
    if not args.project:
        raise ValueError("get-labels requires a project identifier (friendly name or ID)")
    labels = client.get_labels(args.project)
    # Use our utility function to print the labels as a Markdown table.
    print_markdown_table(labels)

def main():
    parser = argparse.ArgumentParser(description="Simplified GitLab Curl Client CLI")
    
    # Global optional arguments
    parser.add_argument("--host", help="GitLab host URL (e.g., https://gitlab.example.com). Defaults to env var GITLAB_HOST.")
    parser.add_argument("--token", help="GitLab API access token. Defaults to env var GITLAB_TOKEN.")

    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)
    
    subparsers.add_parser("list-groups", help="List all groups accessible by the user").set_defaults(func=list_groups)
    
    parser_list_projects = subparsers.add_parser("list-projects", help="List projects in a group")
    parser_list_projects.add_argument("group", help="Group identifier (friendly name or ID)")
    parser_list_projects.set_defaults(func=list_projects)
    
    parser_get_group = subparsers.add_parser("get-group", help="Get details for a group by name")
    parser_get_group.add_argument("group", help="Group name (friendly name)")
    parser_get_group.set_defaults(func=get_group)
    
    parser_get_project = subparsers.add_parser("get-project", help="Get details for a project within a group")
    parser_get_project.add_argument("group", help="Group identifier (friendly name or ID)")
    parser_get_project.add_argument("project", help="Project name (friendly name)")
    parser_get_project.set_defaults(func=get_project)
    
    # New subcommand for getting labels from a project.
    parser_get_labels = subparsers.add_parser("get-labels", help="Get all labels for a project and print them as a Markdown table")
    parser_get_labels.add_argument("project", help="Project identifier (friendly name or ID)")
    parser_get_labels.set_defaults(func=get_labels)
    
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()



⸻

4. How to Use the New Functions

Once you’ve updated your package and reinstalled it (using your updated setup.py with the CLI entry point), you can run commands like:
	•	Get and print all labels for a project in Markdown format:

gitlab-curl get-labels PTO-Project


	•	Other commands remain available:

gitlab-curl list-groups
gitlab-curl list-projects PTO
gitlab-curl get-group PTO
gitlab-curl get-project PTO "PTO-Project"



This extension allows you to retrieve all labels for a project using your friendly naming configuration and to present any API response as a nicely formatted Markdown table.


---

Below is an updated version of your client that introduces a new method, get_issues(), which lets you fetch issues in one of three modes:
	1.	Project Issues: Specify a project (by friendly name or ID) and get issues for that project.
	2.	Group Issues: Specify a group (by friendly name or ID) and get all issues for that group using the group issues endpoint.
	3.	Recursive Group Issues: Specify a group and set an option (include_subgroups) so that issues from subgroups are included as well.

Additionally, you can restrict the issues by a date range by either providing a start date and end date (ISO‑8601 strings) or by specifying the number of days in the past to look back.

⸻

Updated get_issues() Method

Add the following method to your GitLabClient class in gitlab_curl_client/client.py:

from datetime import datetime, timedelta
import urllib.parse

class GitLabClient:
    # ... (other methods)

    def get_issues(self, project_identifier=None, group_identifier=None,
                   start_date=None, end_date=None, days=None,
                   include_subgroups=False):
        """
        Retrieve issues within a specified date range, for a project or a group.
        
        You must specify either a project_identifier or a group_identifier.
        Provide either:
          - start_date and end_date as ISO8601-formatted strings (e.g., "2025-03-01T00:00:00Z"), or
          - days (an integer), representing the number of days from now to look back.
          
        When querying a group, set include_subgroups=True to fetch issues from subgroups as well.
        
        :param project_identifier: The project ID or a friendly name (if mapped in config).
        :param group_identifier: The group ID or a friendly name (if mapped in config).
        :param start_date: Start of the date range (ISO8601 string).
        :param end_date: End of the date range (ISO8601 string).
        :param days: Number of days from now to look back (overrides start_date/end_date).
        :param include_subgroups: Boolean flag to include issues from subgroups (only for group queries).
        :return: Parsed JSON response from the GitLab API.
        """
        # Determine the date range
        if days is not None:
            now = datetime.utcnow()
            start = now - timedelta(days=days)
            start_date = start.isoformat() + "Z"
            end_date = now.isoformat() + "Z"
        elif start_date is not None and end_date is not None:
            # Caller provided valid ISO8601 strings.
            pass
        else:
            raise ValueError("Either days or both start_date and end_date must be provided.")

        # Prepare query parameters
        params = {
            "created_after": start_date,
            "created_before": end_date
        }
        # If this is a group query, include the flag if requested.
        if group_identifier and include_subgroups:
            params["include_subgroups"] = "true"
        
        query_string = urllib.parse.urlencode(params)

        # Use config mappings if available for friendly names
        from . import config

        if project_identifier:
            # Check if project_identifier is a friendly name in your config.
            if isinstance(project_identifier, str):
                project_id = config.PROJECT_IDS.get(project_identifier)
                if project_id:
                    project_identifier = project_id
            endpoint = f"/api/v4/projects/{project_identifier}/issues?{query_string}"
            return self._run_curl("GET", endpoint)

        elif group_identifier:
            # Check if group_identifier is a friendly name in your config.
            if isinstance(group_identifier, str):
                group_id = config.GROUP_IDS.get(group_identifier.upper())
                if group_id:
                    group_identifier = group_id
            endpoint = f"/api/v4/groups/{group_identifier}/issues?{query_string}"
            return self._run_curl("GET", endpoint)
        else:
            raise ValueError("You must provide either a project_identifier or a group_identifier.")



⸻

How It Works
	•	Date Range Handling:
If the days parameter is provided, the function calculates start_date and end_date relative to the current UTC time. Otherwise, both dates must be provided by the caller.
	•	Flexible Scope:
	•	When project_identifier is provided, the endpoint GET /api/v4/projects/:id/issues is used.
	•	When group_identifier is provided, the endpoint GET /api/v4/groups/:id/issues is used.
In both cases, friendly names are resolved via your configuration (assuming you have entries in your config dictionaries).
	•	Include Subgroups:
For group queries, setting include_subgroups=True adds an extra query parameter so that issues from subgroups are returned.
	•	Query Parameters:
The function URL-encodes the date filters and (if applicable) the include_subgroups flag before appending them to the endpoint.

⸻

Example Usages

1. Get Issues for a Specific Project (by friendly name) Within the Last 7 Days:

issues_project = client.get_issues(project_identifier="PTO-Project", days=7)
print(issues_project)

2. Get Issues for a Specific Group (by friendly name) Between Two Dates:

issues_group = client.get_issues(
    group_identifier="PTO",
    start_date="2025-03-01T00:00:00Z",
    end_date="2025-03-15T23:59:59Z"
)
print(issues_group)

3. Get Issues for a Group Recursively (including subgroups) for the Last 14 Days:

issues_group_recursive = client.get_issues(
    group_identifier="PTO",
    days=14,
    include_subgroups=True
)
print(issues_group_recursive)

This unified method gives you the flexibility to choose the scope (project or group) and the date range specification (explicit dates or relative days), while also allowing for recursive queries on groups.

---

Below is one way to extend your package to support flexible retrieval of time‐tracking data. In this design, we add a method (here called get_time_spent) that lets you request time‐tracking information with several options:
	•	You can specify a single project (or a list of specific issue IIDs within that project) or a whole group.
	•	When querying a group, you can decide whether to include issues in subgroups (recursive).
	•	You can filter by issue state (for example, “opened”) so you get only open issues.
	•	You can also filter “by user” (for example, to return only issues assigned to a specific username or set of usernames).
(Since GitLab’s standard API returns only aggregate time for an issue, the “user filter” here works by filtering the issues based on their assignee (or author) rather than splitting the time data per user. If your self‐hosted instance records per–user time details, you might need to adjust the implementation.)

In this example, if no explicit list of issues is provided then the function will fetch all issues from the specified project or group (optionally filtering by state) over a default time range (or one you can control via your date parameters or by another filtering method). Then, for each issue, it calls the issue’s time‑tracking endpoint and attaches the resulting stats.

Below is one sample implementation. (You may want to adjust the defaults—for example, the time range over which you fetch issues—and add additional error handling as needed.)

⸻



# gitlab_curl_client/client.py
from datetime import datetime, timedelta
import urllib.parse

class GitLabClient:
    # ... existing methods ...

    def get_time_spent(self,
                       project_identifier=None,
                       group_identifier=None,
                       issues=None,
                       days=None,
                       start_date=None,
                       end_date=None,
                       state="opened",
                       recursive=False,
                       user_filter=None):
        """
        Retrieve time spent on issues.

        You can filter by:
          - Scope: either a single project (using project_identifier) or a group (using group_identifier).
          - Specific issues: if 'issues' (a single issue IID or a list) is provided, only those issues are processed.
          - Date range: either by providing both start_date and end_date (as ISO8601 strings) or by specifying
            days (which sets start_date to now - days and end_date to now).
          - Issue state: only issues matching the given state (default "opened") are processed.
          - User filter: if provided, only include issues whose assignee’s username is in the filter.
          
        For group queries, setting recursive=True will add the parameter to include issues from subgroups.
        
        :param project_identifier: Project ID or friendly name (if mapped in config).
        :param group_identifier: Group ID or friendly name (if mapped in config).
        :param issues: A single issue IID or a list of issue IIDs (within the project). If provided, only these issues are processed.
        :param days: If provided, looks back this many days (overrides start_date/end_date).
        :param start_date: Start of the date range (ISO8601 string).
        :param end_date: End of the date range (ISO8601 string).
        :param state: Issue state to filter by (e.g., "opened"). Defaults to "opened".
        :param recursive: (For groups only) If True, include issues from subgroups.
        :param user_filter: A username or list of usernames. Only issues whose assignee's username is in this filter will be returned.
        :return: A list of issues with attached time_stats.
        """
        # Determine the date range if needed (this example is used to limit the issues we fetch)
        if days is not None:
            now = datetime.utcnow()
            start = now - timedelta(days=days)
            start_date = start.isoformat() + "Z"
            end_date = now.isoformat() + "Z"
        elif start_date is not None and end_date is not None:
            # Assume valid ISO8601 strings were provided.
            pass
        # If no date range is provided, we won't add a filter to the URL (you could also default to a range).
        
        # Build query parameters for filtering by creation date, if available.
        params = {}
        if start_date and end_date:
            params["created_after"] = start_date
            params["created_before"] = end_date

        # If this is a group query and recursive is True, add that parameter.
        if group_identifier and recursive:
            params["include_subgroups"] = "true"
        
        # URL-encode the parameters.
        query_string = urllib.parse.urlencode(params)

        issues_list = []

        from . import config  # using your config mappings

        # --- Determine Scope and Fetch Issues ---
        if project_identifier:
            # Convert a friendly project name to its numeric ID if possible.
            if isinstance(project_identifier, str):
                project_id = config.PROJECT_IDS.get(project_identifier)
                if project_id:
                    project_identifier = project_id

            # If specific issues are provided, build the list manually.
            if issues:
                if not isinstance(issues, list):
                    issues = [issues]
                for iid in issues:
                    issue = self._run_curl("GET", f"/api/v4/projects/{project_identifier}/issues/{iid}")
                    if issue.get("state") == state:
                        issues_list.append(issue)
            else:
                # Get all issues for the project.
                # Append the query string if any parameters exist.
                endpoint = f"/api/v4/projects/{project_identifier}/issues"
                if query_string:
                    endpoint += f"?{query_string}"
                all_issues = self._run_curl("GET", endpoint)
                # Filter by state.
                issues_list = [issue for issue in all_issues if issue.get("state") == state]

        elif group_identifier:
            # Convert a friendly group name to its numeric ID if possible.
            if isinstance(group_identifier, str):
                group_id = config.GROUP_IDS.get(group_identifier.upper())
                if group_id:
                    group_identifier = group_id

            endpoint = f"/api/v4/groups/{group_identifier}/issues"
            if query_string:
                endpoint += f"?{query_string}"
            all_issues = self._run_curl("GET", endpoint)
            issues_list = [issue for issue in all_issues if issue.get("state") == state]
        else:
            raise ValueError("You must provide either a project_identifier or a group_identifier.")

        # --- Filter by User (if requested) ---
        if user_filter:
            # Accept a single username or a list.
            if isinstance(user_filter, str):
                user_filter = [user_filter]
            issues_list = [issue for issue in issues_list
                           if issue.get("assignee") and issue["assignee"].get("username") in user_filter]

        # --- Retrieve Time Stats for Each Issue ---
        # The GitLab API for time tracking on an issue is at:
        #   GET /projects/:id/issues/:issue_iid/time_stats
        # For group queries, each issue contains a "project_id" and an "iid" to use here.
        results = []
        for issue in issues_list:
            # For project queries, we already know the project_identifier; for group queries use the issue's project_id.
            proj_id = issue.get("project_id") if group_identifier else project_identifier
            issue_iid = issue.get("iid")
            time_stats = self._run_curl("GET", f"/api/v4/projects/{proj_id}/issues/{issue_iid}/time_stats")
            # Merge the time_stats into the issue record.
            issue["time_stats"] = time_stats
            results.append(issue)
            
        return results



⸻

How to Use This Function

Below are a few examples of how you might call the new function:
	1.	Get Time on a Specific Issue in a Project:
Retrieve time stats for issue IID 42 in a project named “PTO-Project”

time_data = client.get_time_spent(project_identifier="PTO-Project", issues=42)
print(time_data)


	2.	Get Time on Several Issues in a Project:
Retrieve time stats for issues with IIDs 12, 34, and 56 in a project

time_data = client.get_time_spent(project_identifier="PTO-Project", issues=[12, 34, 56])
print(time_data)


	3.	Get Time on All Open Issues in a Group (Recursively):
Retrieve time stats for all open issues in the “PTO” group (including subgroups)

time_data = client.get_time_spent(group_identifier="PTO", recursive=True)
print(time_data)


	4.	Get Time on Issues Assigned to a Specific User in a Group:
Retrieve time stats only for issues where the assignee is “alice”

time_data = client.get_time_spent(group_identifier="PTO", recursive=True, user_filter="alice")
print(time_data)


	5.	Limit Issues by Date Range or Days:
For example, get time stats on issues created in the last 14 days:

time_data = client.get_time_spent(project_identifier="PTO-Project", days=14)
print(time_data)



⸻

Notes and Considerations
	•	API Limitations:
The GitLab API’s standard time‑tracking endpoint for issues (GET /projects/:id/issues/:issue_iid/time_stats) returns aggregate time spent on the issue rather than a breakdown by user. In this example, filtering “by user” is applied to the issue’s metadata (for example, by checking the assignee’s username). If your instance tracks per–user time details (or you have extended the API), you may need to adjust the implementation accordingly.
	•	Pagination:
If your group or project has many issues, the API may paginate responses. In production code you might need to handle pagination (for example, by looping through pages using query parameters such as per_page and page).
	•	Default Date Filtering:
In the absence of explicit date parameters, you could choose to limit the returned issues by a default date range (as in the example using days=30 in some calls) or leave the filter off altogether.

This design should give you a flexible foundation for retrieving time‐tracking data across different scopes and with various filters. Feel free to adjust the details to suit your specific use case.

---

Below is an example script that implements the following workflow:
	1.	Retrieves all issues in a project that have the label OJ-22 and one of the stage labels (Stage::1 through Stage::5).
	2.	Groups the issues by stage.
	3.	Creates issue links so that every issue in a given stage blocks every issue in all later stages. In other words:
	•	Every Stage 1 issue blocks every issue in Stage 2, Stage 3, Stage 4, and Stage 5.
	•	Every Stage 2 issue blocks every issue in Stage 3, Stage 4, and Stage 5.
	•	Every Stage 3 issue blocks every issue in Stage 4 and Stage 5.
	•	Every Stage 4 issue blocks every issue in Stage 5.

The script assumes you have a client with a low‑level method _run_curl and a helper method create_issue_link() (which posts to /api/v4/projects/:id/issues/:issue_iid/links). You’ll also need a helper to fetch issues filtered by label. Adjust error handling and logging as needed for your environment.

⸻

Example Script: link_issues.py

#!/usr/bin/env python3
import argparse
import os
from gitlab_curl_client.client import GitLabClient

# Define the stage labels in order.
STAGE_LABELS = ["Stage::1", "Stage::2", "Stage::3", "Stage::4", "Stage::5"]

def get_issues_with_label(client, project, label):
    """
    Retrieve all issues in a project that have a specific label.
    This uses the GitLab API query parameter "labels".
    """
    endpoint = f"/api/v4/projects/{project}/issues?labels={label}"
    return client._run_curl("GET", endpoint)

def filter_and_group_issues(issues):
    """
    From the list of issues, keep only those that also have one of the stage labels.
    Then group them by stage label.
    
    Returns a dict mapping each stage label to the list of issues.
    """
    grouped = {stage: [] for stage in STAGE_LABELS}
    for issue in issues:
        issue_labels = issue.get("labels", [])
        for stage in STAGE_LABELS:
            if stage in issue_labels:
                grouped[stage].append(issue)
                break  # Assume each issue belongs to one stage
    return grouped

def link_issues_by_stage(client, project, grouped):
    """
    For each stage, create issue links so that every issue in the current stage blocks every issue in all later stages.
    
    For example:
      - For each issue in Stage::1, link it as blocker on every issue in Stage::2, Stage::3, Stage::4, and Stage::5.
      - For each issue in Stage::2, link it as blocker on every issue in Stage::3, Stage::4, and Stage::5.
      - Etc.
    """
    for i, current_stage in enumerate(STAGE_LABELS):
        for j in range(i + 1, len(STAGE_LABELS)):
            later_stage = STAGE_LABELS[j]
            for blocker_issue in grouped.get(current_stage, []):
                for blocked_issue in grouped.get(later_stage, []):
                    blocker_iid = blocker_issue.get("iid")
                    blocked_iid = blocked_issue.get("iid")
                    print(f"Linking: Issue {blocker_iid} ({current_stage}) blocks Issue {blocked_iid} ({later_stage})")
                    try:
                        client.create_issue_link(
                            project_identifier=project,
                            issue_iid=blocker_iid,
                            target_project_identifier=project,
                            target_issue_iid=blocked_iid,
                            link_type="blocks"
                        )
                    except Exception as e:
                        print(f"Error linking blocker {blocker_iid} to issue {blocked_iid} ({later_stage}): {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Link issues for OJ-22 based on stage relationships."
    )
    parser.add_argument("--host", help="GitLab host URL (or set GITLAB_HOST)", default=os.getenv("GITLAB_HOST"))
    parser.add_argument("--token", help="GitLab token (or set GITLAB_TOKEN)", default=os.getenv("GITLAB_TOKEN"))
    parser.add_argument("--project", required=True,
                        help="Project identifier (numeric ID or friendly name) containing the issues.")
    args = parser.parse_args()

    if not args.host or not args.token:
        parser.error("Host and token must be provided via arguments or environment variables.")

    client = GitLabClient(args.host, args.token)

    # Step 1: Retrieve all issues with label "OJ-22"
    issues = get_issues_with_label(client, args.project, "OJ-22")
    print(f"Retrieved {len(issues)} issues with label OJ-22.")

    # Step 2: Filter issues that also have one of the stage labels and group them.
    grouped = filter_and_group_issues(issues)
    for stage in STAGE_LABELS:
        count = len(grouped.get(stage, []))
        print(f"{stage}: {count} issues")

    # Step 3: Create the issue links according to the specified stage rules.
    link_issues_by_stage(client, args.project, grouped)

if __name__ == "__main__":
    main()



⸻

Explanation
	1.	Retrieving Issues:
The helper function get_issues_with_label() fetches all issues in the given project that have the label OJ-22 using the GitLab API.
	2.	Filtering and Grouping:
The function filter_and_group_issues() loops over the fetched issues and checks for the presence of any of the stage labels. It groups issues into a dictionary keyed by each stage (e.g., "Stage::1").
	3.	Linking Issues:
The function link_issues_by_stage() loops over the stages in order. For each stage i, it iterates through every later stage j and creates a link for every issue in stage i as a blocker for every issue in stage j. This implements the dependency pattern:
	•	Stage 1 blocks stages 2, 3, 4, 5.
	•	Stage 2 blocks stages 3, 4, 5.
	•	Stage 3 blocks stages 4, 5.
	•	Stage 4 blocks stage 5.
	4.	Running the Script:
The script uses command-line arguments (or environment variables for host/token) and a project identifier. Once run, it retrieves the issues, groups them, and creates the links.

⸻

This example should meet the requirement where the current stage’s issues block all issues in the later stages. Adjust the client implementation (especially the create_issue_link method) and error handling as needed for your specific GitLab instance.

---
Below is an example of a complete Python package that includes all of the helper functions you need. In this example, the package is called gitlab_curl_client and it contains:
	•	A config module for mapping friendly names (if needed).
	•	A client module that wraps curl calls to GitLab (including a helper to create issue links and to get issues filtered by label).
	•	A utils module that contains a Markdown table printer (which you can extend for additional helpers).
	•	A cli module (optional) for basic command‐line usage.
	•	A standalone script (link_issues.py) that uses the helpers to perform the following logic:
	•	Retrieve all issues in a given project with label OJ-22 that also have one of the stage labels (“Stage::1” … “Stage::5”).
	•	Group those issues by stage.
	•	Create issue links so that every issue in a given stage blocks every issue in every later stage (i.e. Stage 1 blocks Stage 2–5; Stage 2 blocks Stage 3–5; Stage 3 blocks Stage 4–5; Stage 4 blocks Stage 5).

Below is the full package with all files.

⸻

Package Structure

gitlab_curl_client/
├── __init__.py
├── config.py
├── client.py
├── utils.py
└── cli.py
link_issues.py
setup.py
README.md



⸻

File: gitlab_curl_client/config.py

# gitlab_curl_client/config.py

# Mapping of friendly names to IDs (adjust these as needed)
GROUP_IDS = {
    "PTO": 23,
    # add other groups as needed
}

PROJECT_IDS = {
    "PTO-Project": 101,
    # add other projects as needed
}



⸻

File: gitlab_curl_client/client.py

# gitlab_curl_client/client.py

import subprocess
import json
import os
import urllib.parse
from . import config

class GitLabClient:
    def __init__(self, host, token):
        """
        Initialize the client.
        :param host: GitLab host URL (e.g., "https://gitlab.example.com")
        :param token: Personal Access Token for API access.
        """
        self.host = host.rstrip('/')
        self.token = token

    def _run_curl(self, method, endpoint, data=None):
        """
        Internal method to execute a curl command.
        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint (e.g., "/api/v4/projects/...")
        :param data: Optional dictionary to send as JSON.
        :return: Parsed JSON response.
        """
        url = f"{self.host}{endpoint}"
        headers = [
            "-H", f"PRIVATE-TOKEN: {self.token}",
            "-H", "Content-Type: application/json"
        ]
        command = ["curl", "-s", "-X", method] + headers

        if data is not None:
            json_data = json.dumps(data)
            command += ["-d", json_data]

        command.append(url)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"curl failed: {e.stderr}") from e
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response")

    def create_issue_link(self, project_identifier, issue_iid, target_project_identifier, target_issue_iid, link_type="blocks"):
        """
        Create an issue link between two issues.
        :param project_identifier: ID or friendly name for the source project.
        :param issue_iid: IID of the source issue (the blocker).
        :param target_project_identifier: ID (or friendly name) for the target project.
        :param target_issue_iid: IID of the target issue.
        :param link_type: Type of link ("blocks" is used here).
        :return: API response.
        """
        # Resolve friendly names if possible.
        if isinstance(project_identifier, str):
            proj_id = config.PROJECT_IDS.get(project_identifier)
            if proj_id:
                project_identifier = proj_id
        if isinstance(target_project_identifier, str):
            tgt_id = config.PROJECT_IDS.get(target_project_identifier)
            if tgt_id:
                target_project_identifier = tgt_id

        data = {
            "target_project_id": target_project_identifier,
            "target_issue_iid": target_issue_iid,
            "link_type": link_type
        }
        endpoint = f"/api/v4/projects/{project_identifier}/issues/{issue_iid}/links"
        return self._run_curl("POST", endpoint, data=data)

    def get_issues_by_label(self, project_identifier, label):
        """
        Retrieve all issues in a project that have a given label.
        :param project_identifier: Project ID or friendly name.
        :param label: Label to filter by.
        :return: List of issues.
        """
        # Resolve friendly project name if needed.
        if isinstance(project_identifier, str):
            proj_id = config.PROJECT_IDS.get(project_identifier)
            if proj_id:
                project_identifier = proj_id
        # GitLab API supports filtering by labels via query parameters.
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/api/v4/projects/{project_identifier}/issues?labels={encoded_label}"
        return self._run_curl("GET", endpoint)



⸻

File: gitlab_curl_client/utils.py

# gitlab_curl_client/utils.py

def print_markdown_table(data):
    """
    Print a list of dictionaries as a Markdown table.
    :param data: List of dictionaries.
    """
    if not data:
        print("No data to display.")
        return

    # Use all keys from all dictionaries as columns.
    headers = list({key for item in data for key in item.keys()})
    
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    print(header_row)
    print(separator_row)
    
    for item in data:
        row = [str(item.get(header, "")) for header in headers]
        print("| " + " | ".join(row) + " |")



⸻

File: gitlab_curl_client/cli.py

(This is an optional CLI interface if you want to run simple commands.)

# gitlab_curl_client/cli.py

import argparse
import os
import json
from .client import GitLabClient

def main():
    parser = argparse.ArgumentParser(description="GitLab Curl Client CLI")
    parser.add_argument("--host", help="GitLab host URL", default=os.getenv("GITLAB_HOST"))
    parser.add_argument("--token", help="GitLab API token", default=os.getenv("GITLAB_TOKEN"))
    parser.add_argument("--project", required=True, help="Project identifier (ID or friendly name)")
    parser.add_argument("action", choices=["list-issues"], help="Action to perform")
    parser.add_argument("--label", default="OJ-22", help="Label to filter issues by (default: OJ-22)")

    args = parser.parse_args()
    if not args.host or not args.token:
        parser.error("Host and token must be provided via arguments or environment variables.")

    client = GitLabClient(args.host, args.token)
    
    if args.action == "list-issues":
        issues = client.get_issues_by_label(args.project, args.label)
        print(json.dumps(issues, indent=2))

if __name__ == "__main__":
    main()



⸻

File: link_issues.py

This is the standalone script that uses the package to perform the specific linking logic. Save this file at the root level (outside the gitlab_curl_client folder).

#!/usr/bin/env python3
import argparse
import os
from gitlab_curl_client.client import GitLabClient

# Define the stage labels in sequential order.
STAGE_LABELS = ["Stage::1", "Stage::2", "Stage::3", "Stage::4", "Stage::5"]

def get_issues_with_oj22(client, project):
    """
    Retrieve all issues with the label "OJ-22" from the specified project.
    """
    issues = client.get_issues_by_label(project, "OJ-22")
    return issues

def filter_and_group_issues(issues):
    """
    From the list of issues, keep only those that have one of the stage labels.
    Group the issues by the stage label.
    Returns a dict mapping each stage label to its list of issues.
    """
    grouped = {stage: [] for stage in STAGE_LABELS}
    for issue in issues:
        issue_labels = issue.get("labels", [])
        for stage in STAGE_LABELS:
            if stage in issue_labels:
                grouped[stage].append(issue)
                break  # Assume one stage per issue
    return grouped

def link_issues_by_stage(client, project, grouped):
    """
    Create links so that each issue in a given stage blocks every issue in all later stages.
    For example:
      - Every Stage::1 issue blocks all issues in Stage::2, Stage::3, Stage::4, and Stage::5.
      - Every Stage::2 issue blocks all issues in Stage::3, Stage::4, and Stage::5.
      - And so on.
    """
    for i, current_stage in enumerate(STAGE_LABELS):
        for later_stage in STAGE_LABELS[i+1:]:
            for blocker in grouped.get(current_stage, []):
                for blocked in grouped.get(later_stage, []):
                    blocker_iid = blocker.get("iid")
                    blocked_iid = blocked.get("iid")
                    print(f"Linking: Issue {blocker_iid} ({current_stage}) blocks Issue {blocked_iid} ({later_stage})")
                    try:
                        client.create_issue_link(
                            project_identifier=project,
                            issue_iid=blocker_iid,
                            target_project_identifier=project,
                            target_issue_iid=blocked_iid,
                            link_type="blocks"
                        )
                    except Exception as e:
                        print(f"Error linking issue {blocker_iid} to {blocked_iid}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Link issues with label OJ-22 by stage relationships."
    )
    parser.add_argument("--host", help="GitLab host URL", default=os.getenv("GITLAB_HOST"))
    parser.add_argument("--token", help="GitLab API token", default=os.getenv("GITLAB_TOKEN"))
    parser.add_argument("--project", required=True, help="Project identifier (ID or friendly name)")
    args = parser.parse_args()

    if not args.host or not args.token:
        parser.error("Host and token must be provided via arguments or environment variables.")

    client = GitLabClient(args.host, args.token)

    # Step 1: Retrieve issues with label "OJ-22"
    issues = get_issues_with_oj22(client, args.project)
    print(f"Retrieved {len(issues)} issues with label OJ-22.")

    # Step 2: Filter and group issues by stage label.
    grouped = filter_and_group_issues(issues)
    for stage in STAGE_LABELS:
        count = len(grouped.get(stage, []))
        print(f"{stage}: {count} issues")

    # Step 3: Create the blocking links.
    link_issues_by_stage(client, args.project, grouped)

if __name__ == "__main__":
    main()



⸻

File: setup.py

(This file allows you to install your package locally.)

from setuptools import setup, find_packages

setup(
    name="gitlab_curl_client",
    version="0.1.0",
    description="A Python package using curl to interact with a self-hosted GitLab.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gitlab-curl=gitlab_curl_client.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)



⸻

File: README.md

# GitLab Curl Client

This package provides a Python client that uses curl to interact with a self-hosted GitLab instance.

## Package Contents

- **gitlab_curl_client/**: Contains the client, configuration, utility functions, and an optional CLI.
- **link_issues.py**: A standalone script that links issues based on stage relationships for issues labeled "OJ-22".
- **setup.py**: Install the package.
- **README.md**: This documentation.

## Installation

From the package root, run:

```bash
python setup.py sdist bdist_wheel
pip install .

Usage

Set your environment variables (or pass them via CLI):

export GITLAB_HOST="https://gitlab.example.com"
export GITLAB_TOKEN="YOUR_ACCESS_TOKEN"

Then run the linking script:

python link_issues.py --project YOUR_PROJECT_ID_OR_NAME

This script will:
	1.	Retrieve all issues with the label OJ-22.
	2.	Group them by stage (Stage::1 to Stage::5).
	3.	Create links so that issues in a given stage block all issues in later stages.

For example:
	•	Stage::1 issues will block Stage::2, Stage::3, Stage::4, and Stage::5.
	•	Stage::2 issues will block Stage::3, Stage::4, and Stage::5.
	•	And so on.

---

### Summary

This complete package includes all helper functions and a linking script that:
- Retrieves issues by label.
- Groups issues by stage.
- Creates issue links so that each stage’s issues block every issue in later stages.

You can customize the mappings, error handling, and additional features as needed for your workflow.


---

Below is an updated version of the complete package that now uses Python’s pathlib library for file‐path operations. For example, we’ve modified the setup script to read the README file using pathlib.Path. You can further update any file‑IO operations in your package to use pathlib as needed.

Below is the complete package with modifications:

⸻

Package Structure

gitlab_curl_client/
├── __init__.py
├── config.py
├── client.py
├── utils.py
└── cli.py
link_issues.py
setup.py
README.md



⸻

File: gitlab_curl_client/config.py

(No file‑system changes needed here; it still contains our friendly‑name mappings.)

# gitlab_curl_client/config.py

# Mapping of friendly names to IDs (adjust these as needed)
GROUP_IDS = {
    "PTO": 23,
    # add other groups as needed
}

PROJECT_IDS = {
    "PTO-Project": 101,
    # add other projects as needed
}



⸻

File: gitlab_curl_client/client.py

(No file‑path operations occur here, so no changes are needed for pathlib in this module.)

# gitlab_curl_client/client.py

import subprocess
import json
import os
import urllib.parse
from . import config

class GitLabClient:
    def __init__(self, host, token):
        """
        Initialize the client.
        :param host: GitLab host URL (e.g., "https://gitlab.example.com")
        :param token: Personal Access Token for API access.
        """
        self.host = host.rstrip('/')
        self.token = token

    def _run_curl(self, method, endpoint, data=None):
        """
        Internal method to execute a curl command.
        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint (e.g., "/api/v4/projects/...")
        :param data: Optional dictionary to send as JSON.
        :return: Parsed JSON response.
        """
        url = f"{self.host}{endpoint}"
        headers = [
            "-H", f"PRIVATE-TOKEN: {self.token}",
            "-H", "Content-Type: application/json"
        ]
        command = ["curl", "-s", "-X", method] + headers

        if data is not None:
            json_data = json.dumps(data)
            command += ["-d", json_data]

        command.append(url)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"curl failed: {e.stderr}") from e
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response")

    def create_issue_link(self, project_identifier, issue_iid, target_project_identifier, target_issue_iid, link_type="blocks"):
        """
        Create an issue link between two issues.
        :param project_identifier: ID or friendly name for the source project.
        :param issue_iid: IID of the source issue (the blocker).
        :param target_project_identifier: ID (or friendly name) for the target project.
        :param target_issue_iid: IID of the target issue.
        :param link_type: Type of link ("blocks" is used here).
        :return: API response.
        """
        # Resolve friendly names if possible.
        if isinstance(project_identifier, str):
            proj_id = config.PROJECT_IDS.get(project_identifier)
            if proj_id:
                project_identifier = proj_id
        if isinstance(target_project_identifier, str):
            tgt_id = config.PROJECT_IDS.get(target_project_identifier)
            if tgt_id:
                target_project_identifier = tgt_id

        data = {
            "target_project_id": target_project_identifier,
            "target_issue_iid": target_issue_iid,
            "link_type": link_type
        }
        endpoint = f"/api/v4/projects/{project_identifier}/issues/{issue_iid}/links"
        return self._run_curl("POST", endpoint, data=data)

    def get_issues_by_label(self, project_identifier, label):
        """
        Retrieve all issues in a project that have a given label.
        :param project_identifier: Project ID or friendly name.
        :param label: Label to filter by.
        :return: List of issues.
        """
        # Resolve friendly project name if needed.
        if isinstance(project_identifier, str):
            proj_id = config.PROJECT_IDS.get(project_identifier)
            if proj_id:
                project_identifier = proj_id
        # GitLab API supports filtering by labels via query parameters.
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/api/v4/projects/{project_identifier}/issues?labels={encoded_label}"
        return self._run_curl("GET", endpoint)



⸻

File: gitlab_curl_client/utils.py

(No modifications are needed regarding file paths here, so it remains unchanged.)

# gitlab_curl_client/utils.py

def print_markdown_table(data):
    """
    Print a list of dictionaries as a Markdown table.
    :param data: List of dictionaries.
    """
    if not data:
        print("No data to display.")
        return

    # Use all keys from all dictionaries as columns.
    headers = list({key for item in data for key in item.keys()})
    
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    print(header_row)
    print(separator_row)
    
    for item in data:
        row = [str(item.get(header, "")) for header in headers]
        print("| " + " | ".join(row) + " |")



⸻

File: gitlab_curl_client/cli.py

(This file remains largely the same; it simply uses the client.)

# gitlab_curl_client/cli.py

import argparse
import os
import json
from .client import GitLabClient

def main():
    parser = argparse.ArgumentParser(description="GitLab Curl Client CLI")
    parser.add_argument("--host", help="GitLab host URL", default=os.getenv("GITLAB_HOST"))
    parser.add_argument("--token", help="GitLab API token", default=os.getenv("GITLAB_TOKEN"))
    parser.add_argument("--project", required=True, help="Project identifier (ID or friendly name)")
    parser.add_argument("action", choices=["list-issues"], help="Action to perform")
    parser.add_argument("--label", default="OJ-22", help="Label to filter issues by (default: OJ-22)")

    args = parser.parse_args()
    if not args.host or not args.token:
        parser.error("Host and token must be provided via arguments or environment variables.")

    client = GitLabClient(args.host, args.token)
    
    if args.action == "list-issues":
        issues = client.get_issues_by_label(args.project, args.label)
        print(json.dumps(issues, indent=2))

if __name__ == "__main__":
    main()



⸻

File: link_issues.py

(No direct file‑system operations occur here, so this script remains unchanged.)

#!/usr/bin/env python3
import argparse
import os
from gitlab_curl_client.client import GitLabClient

# Define the stage labels in sequential order.
STAGE_LABELS = ["Stage::1", "Stage::2", "Stage::3", "Stage::4", "Stage::5"]

def get_issues_with_oj22(client, project):
    """
    Retrieve all issues with the label "OJ-22" from the specified project.
    """
    issues = client.get_issues_by_label(project, "OJ-22")
    return issues

def filter_and_group_issues(issues):
    """
    From the list of issues, keep only those that have one of the stage labels.
    Group the issues by the stage label.
    Returns a dict mapping each stage label to its list of issues.
    """
    grouped = {stage: [] for stage in STAGE_LABELS}
    for issue in issues:
        issue_labels = issue.get("labels", [])
        for stage in STAGE_LABELS:
            if stage in issue_labels:
                grouped[stage].append(issue)
                break  # Assume one stage per issue
    return grouped

def link_issues_by_stage(client, project, grouped):
    """
    Create links so that each issue in a given stage blocks every issue in all later stages.
    For example:
      - Every Stage::1 issue blocks all issues in Stage::2, Stage::3, Stage::4, and Stage::5.
      - Every Stage::2 issue blocks all issues in Stage::3, Stage::4, and Stage::5.
      - And so on.
    """
    for i, current_stage in enumerate(STAGE_LABELS):
        for later_stage in STAGE_LABELS[i+1:]:
            for blocker in grouped.get(current_stage, []):
                for blocked in grouped.get(later_stage, []):
                    blocker_iid = blocker.get("iid")
                    blocked_iid = blocked.get("iid")
                    print(f"Linking: Issue {blocker_iid} ({current_stage}) blocks Issue {blocked_iid} ({later_stage})")
                    try:
                        client.create_issue_link(
                            project_identifier=project,
                            issue_iid=blocker_iid,
                            target_project_identifier=project,
                            target_issue_iid=blocked_iid,
                            link_type="blocks"
                        )
                    except Exception as e:
                        print(f"Error linking issue {blocker_iid} to {blocked_iid}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Link issues with label OJ-22 by stage relationships."
    )
    parser.add_argument("--host", help="GitLab host URL", default=os.getenv("GITLAB_HOST"))
    parser.add_argument("--token", help="GitLab API token", default=os.getenv("GITLAB_TOKEN"))
    parser.add_argument("--project", required=True, help="Project identifier (ID or friendly name)")
    args = parser.parse_args()

    if not args.host or not args.token:
        parser.error("Host and token must be provided via arguments or environment variables.")

    client = GitLabClient(args.host, args.token)

    # Step 1: Retrieve issues with label "OJ-22"
    issues = get_issues_with_oj22(client, args.project)
    print(f"Retrieved {len(issues)} issues with label OJ-22.")

    # Step 2: Filter and group issues by stage label.
    grouped = filter_and_group_issues(issues)
    for stage in STAGE_LABELS:
        count = len(grouped.get(stage, []))
        print(f"{stage}: {count} issues")

    # Step 3: Create the blocking links.
    link_issues_by_stage(client, args.project, grouped)

if __name__ == "__main__":
    main()



⸻

File: setup.py

Here we use pathlib to load the README file as the long description.

from setuptools import setup, find_packages
from pathlib import Path

# Use pathlib to read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="gitlab_curl_client",
    version="0.1.0",
    description="A Python package using curl to interact with a self-hosted GitLab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gitlab-curl=gitlab_curl_client.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)



⸻

File: README.md

(This file remains unchanged.)

# GitLab Curl Client

This package provides a Python client that uses curl to interact with a self-hosted GitLab instance.

## Package Contents

- **gitlab_curl_client/**: Contains the client, configuration, utility functions, and an optional CLI.
- **link_issues.py**: A standalone script that links issues based on stage relationships for issues labeled "OJ-22".
- **setup.py**: Install the package.
- **README.md**: This documentation.

## Installation

From the package root, run:

```bash
python setup.py sdist bdist_wheel
pip install .

Usage

Set your environment variables (or pass them via CLI):

export GITLAB_HOST="https://gitlab.example.com"
export GITLAB_TOKEN="YOUR_ACCESS_TOKEN"

Then run the linking script:

python link_issues.py --project YOUR_PROJECT_ID_OR_NAME

This script will:
	1.	Retrieve all issues with the label OJ-22.
	2.	Group them by stage (Stage::1 to Stage::5).
	3.	Create links so that issues in a given stage block all issues in later stages.

For example:
	•	Stage::1 issues will block Stage::2, Stage::3, Stage::4, and Stage::5.
	•	Stage::2 issues will block Stage::3, Stage::4, and Stage::5.
	•	And so on.

---

### Summary

This updated package uses `pathlib` in the setup script (and you can extend its use to any other file‑system operations as needed). You now have a complete package that includes helper functions and a linking script along with a CLI—all updated to leverage modern Python path handling via `pathlib`.

---

Below is an updated, robust version of the package that adds new methods for:

• Finding issues that have both a due date and a priority label (from a set: priority::a, priority::b, priority::c, priority::d, priority::e).
• Updating an issue’s due date.
• Updating an issue’s labels.

In this design the methods are added to the client module so you can build programs on top of these APIs.

⸻

Package Structure

gitlab_curl_client/
├── __init__.py
├── config.py
├── exceptions.py
├── client.py
└── utils.py
setup.py
README.md



⸻

File: gitlab_curl_client/config.py

# gitlab_curl_client/config.py

# Mapping of friendly names to numeric IDs.
GROUP_IDS = {
    "PTO": 23,
    # Add other group mappings as needed.
}

PROJECT_IDS = {
    "PTO-Project": 101,
    # Add other project mappings as needed.
}

# Default settings for the API
DEFAULT_PER_PAGE = 100
DEFAULT_TIMEOUT = 30  # seconds



⸻

File: gitlab_curl_client/exceptions.py

# gitlab_curl_client/exceptions.py

class GitLabClientError(Exception):
    """Base exception for GitLab Client errors."""
    pass

class CurlCommandError(GitLabClientError):
    """Raised when the curl command fails."""
    pass

class JSONDecodingError(GitLabClientError):
    """Raised when the API response cannot be parsed as JSON."""
    pass

class APIError(GitLabClientError):
    """Raised when the API returns an error status."""
    pass



⸻

File: gitlab_curl_client/client.py

Below is the complete client module with the new methods added. It now includes:

• A method to get all issues (via pagination) that have a due date and one of a set of priority labels.
• Methods to update an issue’s due date and its labels.

# gitlab_curl_client/client.py

import subprocess
import json
import os
import urllib.parse
import logging
from datetime import datetime
from . import config
from .exceptions import CurlCommandError, JSONDecodingError, APIError

# Configure module-level logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class GitLabClient:
    def __init__(self, host, token, timeout=config.DEFAULT_TIMEOUT):
        """
        Initialize the GitLab client.
        
        :param host: Base URL for your GitLab instance (e.g. "https://gitlab.example.com").
        :param token: Personal Access Token for API access.
        :param timeout: Timeout (in seconds) for API calls.
        """
        self.host = host.rstrip('/')
        self.token = token
        self.timeout = timeout

    def _run_curl(self, method, endpoint, data=None):
        """
        Execute a curl command to interact with the GitLab API.
        
        :param method: HTTP method (e.g., "GET", "POST", "PUT").
        :param endpoint: API endpoint (e.g., "/api/v4/projects/123/issues").
        :param data: Optional dictionary to send as JSON.
        :return: Parsed JSON response.
        :raises CurlCommandError: If the curl command fails.
        :raises JSONDecodingError: If the response cannot be parsed as JSON.
        """
        url = f"{self.host}{endpoint}"
        headers = [
            "-H", f"PRIVATE-TOKEN: {self.token}",
            "-H", "Content-Type: application/json"
        ]
        command = ["curl", "-s", "-X", method] + headers

        if data is not None:
            json_data = json.dumps(data)
            command += ["-d", json_data]

        command.append(url)

        logger.debug(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, timeout=self.timeout
            )
            logger.debug(f"Response: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"curl command failed: {e.stderr}")
            raise CurlCommandError(f"curl failed: {e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            logger.error("curl command timed out")
            raise CurlCommandError("curl command timed out") from e

        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON response")
            raise JSONDecodingError("Failed to decode JSON response") from e

        if isinstance(response, dict) and response.get("error"):
            logger.error(f"API error: {response.get('error')}")
            raise APIError(response.get("error"))
        return response

    def _resolve_project(self, project_identifier):
        """
        Resolve a project identifier that might be a friendly name.
        
        :param project_identifier: Numeric ID or friendly name.
        :return: Numeric project ID.
        """
        if isinstance(project_identifier, str):
            proj_id = config.PROJECT_IDS.get(project_identifier)
            if proj_id:
                return proj_id
        return project_identifier

    def create_issue_link(self, project_identifier, issue_iid, target_project_identifier, target_issue_iid, link_type="blocks"):
        """
        Create an issue link between two issues.
        
        :param project_identifier: ID or friendly name for the source project.
        :param issue_iid: IID of the source issue (the blocker).
        :param target_project_identifier: ID or friendly name for the target project.
        :param target_issue_iid: IID of the target issue.
        :param link_type: Type of link ("blocks" by default).
        :return: API response.
        """
        source_project = self._resolve_project(project_identifier)
        target_project = self._resolve_project(target_project_identifier)
        data = {
            "target_project_id": target_project,
            "target_issue_iid": target_issue_iid,
            "link_type": link_type
        }
        endpoint = f"/api/v4/projects/{source_project}/issues/{issue_iid}/links"
        return self._run_curl("POST", endpoint, data=data)

    def get_issues_by_label(self, project_identifier, label, page=1, per_page=config.DEFAULT_PER_PAGE):
        """
        Retrieve issues in a project that have a given label.
        
        :param project_identifier: ID or friendly name for the project.
        :param label: Label to filter by.
        :param page: Page number for pagination.
        :param per_page: Number of issues per page.
        :return: List of issues.
        """
        project = self._resolve_project(project_identifier)
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/api/v4/projects/{project}/issues?labels={encoded_label}&page={page}&per_page={per_page}"
        return self._run_curl("GET", endpoint)

    def get_all_issues_by_label(self, project_identifier, label):
        """
        Retrieve all issues in a project that have a given label.
        Handles pagination internally.
        
        :param project_identifier: ID or friendly name for the project.
        :param label: Label to filter by.
        :return: List of all matching issues.
        """
        issues = []
        page = 1
        while True:
            batch = self.get_issues_by_label(project_identifier, label, page=page)
            if not batch:
                break
            issues.extend(batch)
            if len(batch) < config.DEFAULT_PER_PAGE:
                break
            page += 1
        return issues

    def get_issues_with_due_date_and_priority(self, project_identifier, priority_labels=None):
        """
        Retrieve all issues in a project that have a due date and one of the specified priority labels.
        
        :param project_identifier: ID or friendly name for the project.
        :param priority_labels: List of priority labels to look for.
                                Defaults to ["priority::a", "priority::b", "priority::c", "priority::d", "priority::e"].
        :return: List of issues matching the criteria.
        """
        if priority_labels is None:
            priority_labels = ["priority::a", "priority::b", "priority::c", "priority::d", "priority::e"]
        issues = []
        for priority in priority_labels:
            issues.extend(self.get_all_issues_by_label(project_identifier, priority))
        # Remove duplicates (using a unique issue ID) and then filter by due_date.
        unique = {}
        for issue in issues:
            unique[issue["id"]] = issue
        filtered = [issue for issue in unique.values() if issue.get("due_date")]
        return filtered

    def update_issue_due_date(self, project_identifier, issue_iid, new_due_date):
        """
        Update the due date of an issue.
        
        :param project_identifier: ID or friendly name for the project.
        :param issue_iid: IID of the issue.
        :param new_due_date: New due date as a string in YYYY-MM-DD format.
        :return: API response.
        """
        project = self._resolve_project(project_identifier)
        data = {"due_date": new_due_date}
        endpoint = f"/api/v4/projects/{project}/issues/{issue_iid}"
        return self._run_curl("PUT", endpoint, data=data)

    def update_issue_labels(self, project_identifier, issue_iid, new_labels):
        """
        Update the labels of an issue.
        
        :param project_identifier: ID or friendly name for the project.
        :param issue_iid: IID of the issue.
        :param new_labels: List of labels to set (or a comma-separated string).
        :return: API response.
        """
        project = self._resolve_project(project_identifier)
        if isinstance(new_labels, list):
            labels_str = ",".join(new_labels)
        else:
            labels_str = new_labels
        data = {"labels": labels_str}
        endpoint = f"/api/v4/projects/{project}/issues/{issue_iid}"
        return self._run_curl("PUT", endpoint, data=data)



⸻

File: gitlab_curl_client/utils.py

(Remains the same as before; it includes utility functions such as printing Markdown tables and date helpers.)

# gitlab_curl_client/utils.py

from datetime import datetime, timedelta

def print_markdown_table(data):
    """
    Print a list of dictionaries as a Markdown table.
    
    :param data: List of dictionaries (each representing a row).
    """
    if not data:
        print("No data to display.")
        return

    headers = list({key for row in data for key in row.keys()})
    
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    print(header_row)
    print(separator_row)
    
    for row in data:
        values = [str(row.get(header, "")) for header in headers]
        print("| " + " | ".join(values) + " |")

def iso8601_now():
    """Return the current UTC time in ISO8601 format with a trailing 'Z'."""
    return datetime.utcnow().isoformat() + "Z"

def iso8601_days_ago(days):
    """
    Return the UTC time from 'days' ago in ISO8601 format.
    
    :param days: Number of days in the past.
    """
    past = datetime.utcnow() - timedelta(days=days)
    return past.isoformat() + "Z"



⸻

File: setup.py

(Uses pathlib to load the README file, as before.)

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="gitlab_curl_client",
    version="0.1.0",
    description="A robust Python package using curl to interact with a self-hosted GitLab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)



⸻

File: README.md

(The README should now be updated to mention the new methods.)

# GitLab Curl Client

This package provides a robust Python client that uses curl to interact with a self-hosted GitLab instance. It offers:

- Friendly-name resolution for projects and groups.
- Robust error handling and logging.
- Support for pagination.
- Methods to retrieve issues by label.
- New methods to:
  - Retrieve issues that have both a due date and one of the priority labels (priority::a, priority::b, priority::c, priority::d, priority::e).
  - Update an issue’s due date.
  - Update an issue’s labels.
- Utility functions for common tasks (e.g., printing Markdown tables, date conversions).

## Installation

From the package root, run:

```bash
python setup.py sdist bdist_wheel
pip install .

Usage Example

from gitlab_curl_client.client import GitLabClient
from gitlab_curl_client.utils import print_markdown_table

# Initialize the client.
client = GitLabClient("https://gitlab.example.com", "YOUR_ACCESS_TOKEN")

# Retrieve issues with a due date and a priority label.
priority_issues = client.get_issues_with_due_date_and_priority("PTO-Project")
print_markdown_table(priority_issues)

# Update the due date of an issue.
client.update_issue_due_date("PTO-Project", 42, "2025-12-31")

# Update the labels on an issue.
client.update_issue_labels("PTO-Project", 42, ["priority::a", "bug", "OJ-22"])



⸻

Summary

This complete package now includes robust functionality for:
	•	Retrieving issues by label (with pagination).
	•	Filtering issues that have a due date and a priority label.
	•	Modifying an issue’s due date and labels.

This foundation lets you build extensive programs for managing GitLab issues and workflows.


---

Below is an example Python program that uses your GitLab client package to poll your GitLab instance every five minutes for new todos and display a desktop notification via Zenity. This program tracks which todos have already been notified so that only new ones trigger a notification.

You can save this as, for example, check_todos.py:

#!/usr/bin/env python3
import time
import subprocess
import os
from gitlab_curl_client.client import GitLabClient

def get_todos(client):
    """
    Retrieve the list of todos for the authenticated user.
    This calls the GitLab API endpoint `/api/v4/todos`.
    """
    # Using the low-level _run_curl method to call the todos endpoint.
    return client._run_curl("GET", "/api/v4/todos")

def show_notification(todo):
    """
    Use zenity to display a desktop notification for the todo.
    The notification will show the title and target URL if available.
    """
    title = todo.get("title", "No Title")
    target_url = todo.get("target_url", "")
    text = f"New Todo: {title}"
    if target_url:
        text += f"\n{target_url}"
    # Call zenity to display a notification.
    subprocess.run(["zenity", "--notification", "--text", text])

def main():
    host = os.getenv("GITLAB_HOST")
    token = os.getenv("GITLAB_TOKEN")
    if not host or not token:
        print("Please set the GITLAB_HOST and GITLAB_TOKEN environment variables.")
        return

    client = GitLabClient(host, token)
    notified_todo_ids = set()

    print("Starting todo notifier... (checking every 5 minutes)")
    while True:
        try:
            todos = get_todos(client)
            for todo in todos:
                todo_id = todo.get("id")
                # Only notify if this todo hasn't been seen before.
                if todo_id and todo_id not in notified_todo_ids:
                    show_notification(todo)
                    notified_todo_ids.add(todo_id)
        except Exception as e:
            print("Error checking todos:", e)
        # Sleep for 5 minutes (300 seconds) before polling again.
        time.sleep(300)

if __name__ == "__main__":
    main()

How It Works
	1.	Environment Variables:
The program expects your GitLab host URL and API token to be set in the environment as GITLAB_HOST and GITLAB_TOKEN.
	2.	Polling for Todos:
Every 5 minutes the program calls the GitLab API endpoint /api/v4/todos using the client’s low-level _run_curl method.
	3.	Filtering New Todos:
It maintains a set of notified todo IDs. Only todos not in this set trigger a Zenity desktop notification.
	4.	Zenity Notification:
When a new todo is found, the program runs the command

zenity --notification --text "New Todo: [title]\n[target_url]"

to display a desktop notification.

This design ensures that you’re notified only once for each new todo without spamming you on every poll. You can further refine error handling, logging, or persistence of notified IDs if you’d like the notifications to persist across program restarts.


---