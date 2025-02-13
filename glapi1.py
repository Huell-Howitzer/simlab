import subprocess
import json
import csv

def get_gitlab_issues(group_id, gitlab_url, private_token, output_csv="gitlab_issues.csv"):
    """
    Fetch all issues from a GitLab group, including its projects and subprojects, and export them to a CSV file.

    Args:
        group_id (int or str): GitLab group ID or path (e.g., "mygroup").
        gitlab_url (str): The base URL of the GitLab instance (e.g., "https://gitlab.example.com").
        private_token (str): A GitLab personal access token with read_api permissions.
        output_csv (str): Output CSV file path (default: "gitlab_issues.csv").
    """
    # GitLab API headers
    headers = ["PRIVATE-TOKEN: " + private_token]

    # Get all projects under the group (including subgroups)
    projects_api_url = f"{gitlab_url}/api/v4/groups/{group_id}/projects?per_page=100"

    try:
        # Fetch projects
        result = subprocess.run(
            ["curl", "-s", "-H", headers[0], projects_api_url],
            capture_output=True, text=True, check=True
        )
        projects = json.loads(result.stdout)

        if not projects:
            print("No projects found in the group.")
            return

        issues_data = []

        # Loop through all projects and fetch issues
        for project in projects:
            project_id = project["id"]
            project_name = project["name"]
            issues_api_url = f"{gitlab_url}/api/v4/projects/{project_id}/issues?per_page=100"

            result = subprocess.run(
                ["curl", "-s", "-H", headers[0], issues_api_url],
                capture_output=True, text=True, check=True
            )
            issues = json.loads(result.stdout)

            for issue in issues:
                issues_data.append({
                    "Project": project_name,
                    "Issue ID": issue["id"],
                    "Title": issue["title"],
                    "Description": issue.get("description", "").replace("\n", " "),
                    "State": issue["state"],  # Open or Closed
                    "Start Date": issue.get("created_at", "N/A"),
                    "Due Date": issue.get("due_date", "N/A"),
                    "Time Estimate (sec)": issue.get("time_stats", {}).get("time_estimate", 0),
                    "Time Spent (sec)": issue.get("time_stats", {}).get("total_time_spent", 0),
                    "Weight": issue.get("weight", "N/A"),
                    "Labels": ", ".join(issue.get("labels", []))
                })

        # Save to CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Project", "Issue ID", "Title", "Description", "State", 
                "Start Date", "Due Date", "Time Estimate (sec)", "Time Spent (sec)", 
                "Weight", "Labels"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(issues_data)

        print(f"Issues exported to {output_csv}")

    except subprocess.CalledProcessError as e:
        print(f"Error fetching data: {e.stderr.strip()}")
    except json.JSONDecodeError:
        print("Failed to parse API response. Check token or GitLab URL.")

# Example usage
gitlab_url = "https://gitlab.example.com"
private_token = "your_private_token"
group_id = "your-group-id"

get_gitlab_issues(group_id, gitlab_url, private_token)