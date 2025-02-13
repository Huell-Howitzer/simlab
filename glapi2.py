import subprocess
import json

def get_gitlab_last_login(username, gitlab_url, private_token):
    """
    Get the last login time of a GitLab user using subprocess and curl.

    Args:
        username (str): The GitLab username to check.
        gitlab_url (str): The base URL of the GitLab instance (e.g., "https://gitlab.example.com").
        private_token (str): A GitLab personal access token with admin privileges.

    Returns:
        str: Last login timestamp or an error message.
    """
    try:
        # API endpoint to fetch all users (or consider filtering in the API call)
        api_url = f"{gitlab_url}/api/v4/users?username={username}"

        # Run curl command to get user details
        result = subprocess.run(
            ["curl", "-s", "-H", f"PRIVATE-TOKEN: {private_token}", api_url],
            capture_output=True, text=True, check=True
        )

        # Parse JSON response
        users = json.loads(result.stdout)

        if users:
            last_login = users[0].get("last_sign_in_at", "Never logged in")
            return f"Last login for {username}: {last_login}"
        else:
            return f"User '{username}' not found."

    except subprocess.CalledProcessError as e:
        return f"Error fetching last login: {e.stderr.strip()}"
    except json.JSONDecodeError:
        return "Failed to parse response. Check API token or GitLab URL."

# Example usage
gitlab_url = "https://gitlab.example.com"
private_token = "your_private_token"
username = "someuser"

print(get_gitlab_last_login(username, gitlab_url, private_token))