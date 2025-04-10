Got it — that’s a detailed and solid plan. Here’s a Python script that:
	1.	Gets all issues in a GitLab group.
	2.	Finds issues with both Event::OJ::X and Stage::Y labels.
	3.	Finds a milestone titled OJ-X Stage Y: ... and assigns the issue to it.
	4.	Builds a dependency graph per OJ-X group so that Stage 1 blocks 2–5, Stage 2 blocks 3–5, etc., within the same OJ-X group.

Let’s break it into a working script:

⸻

Python Script

import requests
import re
from collections import defaultdict

ACCESS_TOKEN = 'your_access_token'
GROUP_ID = 'your_group_id_or_path'
GITLAB_URL = 'https://gitlab.com'
HEADERS = {'Private-Token': ACCESS_TOKEN}
ISSUES_URL = f"{GITLAB_URL}/api/v4/groups/{GROUP_ID}/issues"
MILESTONES_URL = f"{GITLAB_URL}/api/v4/groups/{GROUP_ID}/milestones"
UPDATE_ISSUE_URL = f"{GITLAB_URL}/api/v4/projects/{{project_id}}/issues/{{issue_iid}}"
BLOCKING_URL = f"{GITLAB_URL}/api/v4/projects/{{project_id}}/issues/{{source_iid}}/block"

def get_all_pages(url, params=None):
    results = []
    page = 1
    while True:
        p = params.copy() if params else {}
        p.update({'page': page, 'per_page': 100})
        r = requests.get(url, headers=HEADERS, params=p)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return results

# Step 1: Get all milestones
milestones = get_all_pages(MILESTONES_URL)
milestone_map = {}
for m in milestones:
    match = re.match(r'OJ-(\d{1,2}) Stage (\d):', m['title'])
    if match:
        oj, stage = match.groups()
        milestone_map[(f"OJ-{oj}", f"Stage::{stage}")] = m['id']

# Step 2: Get all issues in group
issues = get_all_pages(ISSUES_URL)

# Step 3: Organize issues by OJ-X and Stage
oj_stage_issues = defaultdict(lambda: defaultdict(list))

for issue in issues:
    labels = issue.get('labels', [])
    project_id = issue['project_id']
    iid = issue['iid']

    event_label = next((l for l in labels if re.match(r'Event::OJ::\d{1,2}', l)), None)
    stage_label = next((l for l in labels if re.match(r'Stage::[1-5]', l)), None)

    if not (event_label and stage_label):
        continue

    oj_x = event_label.replace('Event::', '').replace('::', '-')
    stage = stage_label

    # Match milestone
    milestone_id = milestone_map.get((oj_x, stage))
    if milestone_id:
        # Assign milestone to issue
        update_url = UPDATE_ISSUE_URL.format(project_id=project_id, issue_iid=iid)
        requests.put(update_url, headers=HEADERS, json={'milestone_id': milestone_id})

    # Organize for dependencies
    oj_stage_issues[oj_x][stage].append({
        'id': issue['id'],
        'project_id': project_id,
        'iid': iid
    })

# Step 4: Add blocking relationships
stage_order = ['Stage::1', 'Stage::2', 'Stage::3', 'Stage::4', 'Stage::5']

for oj_x, stages in oj_stage_issues.items():
    for i, blocker_stage in enumerate(stage_order[:-1]):
        for blockee_stage in stage_order[i+1:]:
            blockers = stages.get(blocker_stage, [])
            blockees = stages.get(blockee_stage, [])
            for blocker in blockers:
                for blockee in blockees:
                    # Add blocking relationship
                    url = BLOCKING_URL.format(
                        project_id=blocker['project_id'],
                        source_iid=blocker['iid']
                    )
                    try:
                        requests.post(url, headers=HEADERS, json={
                            'target_project_id': blockee['project_id'],
                            'target_issue_iid': blockee['iid']
                        })
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 409:
                            continue  # Already exists
                        else:
                            print(f"Error linking issues: {e}")

print("Done.")



⸻

Key Points:
	•	Regex matching is used to detect Event::OJ::X and Stage::Y labels.
	•	Milestone assignment uses matching pattern OJ-X Stage Y: ....
	•	Dependencies are set only within the same OJ-X, respecting stage order strictly.
	•	Uses requests.put() to update issues and requests.post() to set blockers via the GitLab API.

⸻

Would you like me to turn this into a CLI tool or give it logging/output enhancements next?