import os
import time
import random
import requests
import socket
import subprocess
import traceback
import shutil

# === CONFIGURATION ===
GITLAB_URL = "https://gitlab.example.com"  # Replace with your instance
PROJECT_ID = 12345                         # Replace with your project ID
PRIVATE_TOKEN = "your_private_token"       # Replace with your token
LOGGING_ISSUE_ID = 9999                    # Replace with your monitoring/logging issue ID

LABEL_HELP = "Help"
LABEL_IN_PROGRESS = "In Progress"
LABEL_COMPLETED = "Completed"
POLL_INTERVAL_SECONDS = 60
POLL_JITTER_SECONDS = 480  # Up to 8 minutes jitter
CLAIM_BACKOFF_SECONDS = 5  # Random delay before claiming
RECHECK_DELAY_SECONDS = 2  # Delay before re-checking script existence

HEADERS = {"PRIVATE-TOKEN": PRIVATE_TOKEN}
MACHINE_ID = socket.gethostname()


# === CORE FUNCTIONS ===

def get_open_help_issues():
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/issues"
    params = {"state": "opened", "labels": LABEL_HELP, "per_page": 10}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return [
        issue for issue in response.json()
        if LABEL_IN_PROGRESS not in issue["labels"] and LABEL_COMPLETED not in issue["labels"]
    ]


def update_labels(issue_id, add=None, remove=None):
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/issues/{issue_id}"
    issue = requests.get(url, headers=HEADERS).json()
    current_labels = set(issue["labels"])
    if add:
        current_labels.update(add)
    if remove:
        current_labels.difference_update(remove)
    payload = {"labels": ",".join(current_labels)}
    requests.put(url, headers=HEADERS, data=payload)


def close_issue(issue_id):
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/issues/{issue_id}"
    requests.put(url, headers=HEADERS, data={"state_event": "close"})


def post_comment(issue_id, message):
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/issues/{issue_id}/notes"
    data = {"body": message}
    response = requests.post(url, headers=HEADERS, data=data)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post comment: {response.status_code} {response.text}")


def format_exception(e):
    return f"Machine: `{MACHINE_ID}`\nTime: `{time.ctime()}`\nError:\n```\n{traceback.format_exc()}\n```"


def parse_paths(description):
    lines = [line.strip() for line in description.splitlines() if line.strip()]
    paths = [line for line in lines if os.path.exists(line)]

    if len(paths) == 1 and os.path.isfile(paths[0]):
        file_path = os.path.abspath(paths[0])
        dir_path = os.path.dirname(os.path.abspath(__file__))
    elif len(paths) >= 2:
        dir_path = os.path.abspath(paths[0])
        file_path = os.path.abspath(paths[1])
    else:
        raise ValueError("Could not determine valid directory and file path.")

    if not os.path.isdir(dir_path):
        raise ValueError(f"Invalid directory path: {dir_path}")

    return dir_path, file_path


def safe_rename_script(file_path, issue_id):
    """
    Ensures the script can be executed safely:
    - If file exists, wait and check again.
    - If still exists, rename to .in_progress and return new path.
    - If it's gone but .in_progress exists, assume another agent claimed it.
    - If both missing: error.
    """
    in_progress_path = file_path + ".in_progress"

    if not os.path.exists(file_path):
        if os.path.exists(in_progress_path):
            print("Script is already in progress by another runner.")
            return None
        raise FileNotFoundError(f"Script {file_path} missing and .in_progress not found.")

    time.sleep(random.uniform(0.5, RECHECK_DELAY_SECONDS))

    if not os.path.exists(file_path):
        if os.path.exists(in_progress_path):
            print("Script was already renamed by another runner.")
            return None
        raise FileNotFoundError(f"Script {file_path} disappeared unexpectedly.")

    # Rename script to .in_progress to claim it
    shutil.move(file_path, in_progress_path)
    print(f"Renamed {file_path} to {in_progress_path}")
    return in_progress_path


def run_script(dir_path, script_path):
    print(f"Running script {script_path} in directory {dir_path}")
    subprocess.run(["python3", script_path], cwd=dir_path, check=True)


# === MAIN LOOP ===

if __name__ == "__main__":
    while True:
        try:
            issues = get_open_help_issues()
            if not issues:
                print("No eligible issues found.")
            else:
                issue = issues[0]
                issue_id = issue["iid"]
                print(f"Found eligible issue #{issue_id}: {issue['title']}")

                delay = random.uniform(0, CLAIM_BACKOFF_SECONDS)
                print(f"Sleeping {delay:.2f} seconds before attempting to claim...")
                time.sleep(delay)

                latest = requests.get(
                    f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/issues/{issue_id}",
                    headers=HEADERS
                ).json()

                if LABEL_IN_PROGRESS in latest["labels"] or LABEL_COMPLETED in latest["labels"]:
                    print(f"Issue #{issue_id} already claimed. Skipping.")
                else:
                    update_labels(issue_id, add={LABEL_IN_PROGRESS})

                    try:
                        dir_path, file_path = parse_paths(issue["description"])
                        claimed_script = safe_rename_script(file_path, issue_id)
                        if claimed_script is None:
                            continue  # Someone else got it
                        run_script(dir_path, claimed_script)
                        update_labels(issue_id, add={LABEL_COMPLETED}, remove={LABEL_IN_PROGRESS})
                        close_issue(issue_id)
                        print(f"Issue #{issue_id} completed and closed.")
                    except Exception as script_error:
                        print(f"[SCRIPT ERROR] {script_error}")
                        post_comment(issue_id, f":x: Script execution error:\n{format_exception(script_error)}")

        except Exception as general_error:
            print(f"[ERROR] {general_error}")
            post_comment(LOGGING_ISSUE_ID, f":warning: General error occurred:\n{format_exception(general_error)}")

        sleep_duration = POLL_INTERVAL_SECONDS + random.uniform(0, POLL_JITTER_SECONDS)
        print(f"Sleeping {sleep_duration:.2f} seconds until next poll...")
        time.sleep(sleep_duration)