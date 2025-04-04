Here’s a clear, complete, and consolidated example covering all your requirements:
	•	Matching Issues to Epics (Event::OJ::X labels).
	•	Matching Issues to Milestones (Event::OJ::X & Stage::Y labels).
	•	Searching for issues by title text and moving them to another project.

⸻

Complete Python Script

import pandas as pd
import requests
import re

# Your GitLab setup
GITLAB_URL = "https://gitlab.com/api/v4"
PRIVATE_TOKEN = "YOUR_GITLAB_TOKEN"
PROJECT_ID = "YOUR_SOURCE_PROJECT_ID"
DEST_PROJECT_ID = "YOUR_DEST_PROJECT_ID"  # For moving issues between projects
GROUP_ID = "YOUR_GROUP_ID"

headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

# --- Helper Functions ---

def assign_issue_to_epic(issue_iid, epic_id):
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues/{issue_iid}"
    response = requests.put(url, headers=headers, data={'epic_id': epic_id})
    return response.ok, response.json()

def assign_issue_to_milestone(issue_iid, milestone_id):
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues/{issue_iid}"
    response = requests.put(url, headers=headers, data={'milestone_id': milestone_id})
    return response.ok, response.json()

def move_issue_to_project(issue_iid, dest_project_id):
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues/{issue_iid}/move"
    response = requests.post(url, headers=headers, data={'to_project_id': dest_project_id})
    return response.ok, response.json()

def search_issues_by_title(title_substring):
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues"
    params = {'search': title_substring, 'in': 'title'}
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.ok else []

# --- Data Preparation and Matching Logic ---

# Assuming you already have these DataFrames:
# df_epics, df_issues, df_milestones

# Extract relevant labels for epics, issues, milestones
def extract_label(labels, prefix):
    return next((label for label in labels if label.startswith(prefix)), None)

# Prepare Epics
df_epics['event_label'] = df_epics['labels'].apply(lambda x: extract_label(x, 'Event::OJ::'))

# Prepare Issues
df_issues['event_label'] = df_issues['labels'].apply(lambda x: extract_label(x, 'Event::OJ::'))
df_issues['stage_label'] = df_issues['labels'].apply(lambda x: extract_label(x, 'Stage::'))

# Prepare Milestones (parse titles)
def parse_milestone_title(title):
    match = re.match(r"(OJ-\d+)\s+(Stage\s+\d+):", title)
    if match:
        event_label = f"Event::{match.group(1).replace('-', '::')}"
        stage_label = match.group(2).replace(' ', '::')
        return event_label, stage_label
    return None, None

df_milestones[['event_label', 'stage_label']] = df_milestones['title'].apply(
    lambda x: pd.Series(parse_milestone_title(x))
)

# --- Associate Issues to Epics ---
df_issues = pd.merge(
    df_issues,
    df_epics[['epic_id', 'event_label']],
    on='event_label',
    how='left'
)

# Update GitLab: assign issues to epics
for idx, row in df_issues.iterrows():
    if pd.notna(row['epic_id']):
        success, _ = assign_issue_to_epic(row['issue_id'], int(row['epic_id']))
        print(f"Issue {row['issue_id']} to Epic {row['epic_id']}: {'Success' if success else 'Failed'}")

# --- Associate Issues to Milestones ---
df_issues = pd.merge(
    df_issues,
    df_milestones[['milestone_id', 'event_label', 'stage_label']],
    on=['event_label', 'stage_label'],
    how='left'
)

# Update GitLab: assign issues to milestones
for idx, row in df_issues.iterrows():
    if pd.notna(row['milestone_id']):
        success, _ = assign_issue_to_milestone(row['issue_id'], int(row['milestone_id']))
        print(f"Issue {row['issue_id']} to Milestone {row['milestone_id']}: {'Success' if success else 'Failed'}")

# --- Search and Move Issues by Title ---
def search_and_move_issues(title_substring, dest_project_id):
    matches = search_issues_by_title(title_substring)
    if not matches:
        print("No matching issues found.")
        return
    
    for issue in matches:
        issue_iid = issue['iid']
        success, response = move_issue_to_project(issue_iid, dest_project_id)
        print(f"Moving Issue {issue_iid} '{issue['title']}': {'Success' if success else f'Failed ({response})'}")

# Example Usage:
search_and_move_issues("text to find", DEST_PROJECT_ID)



⸻

What This Script Does:
	•	Assigns Issues to Epics based on matching Event::OJ::X labels.
	•	Assigns Issues to Milestones based on both Event::OJ::X and Stage::Y labels.
	•	Provides a convenient function to search for issues by title and move them to another GitLab project.

⸻

How to Use:
	•	Replace placeholders (YOUR_GITLAB_TOKEN, YOUR_SOURCE_PROJECT_ID, YOUR_DEST_PROJECT_ID, YOUR_GROUP_ID) with your GitLab details.
	•	Ensure your DataFrames (df_epics, df_issues, and df_milestones) are populated correctly from GitLab data.
	•	Adjust the label extraction logic if your labels differ.

This comprehensive script provides a structured, easy-to-maintain solution, meeting all your stated requirements.