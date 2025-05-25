```python
import gitlab
import requests
import re
from pathlib import Path

# CONFIGURATION
GITLAB_URL = 'https://gitlab.com'
PRIVATE_TOKEN = 'YOUR_ACCESS_TOKEN'
PROJECT_ID = 'your-project-id'
MAIN_BRANCH = 'main'
SOURCE_BRANCH = 'feature-branch'
TIMEOUT = 5

# Setup GitLab
gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
project = gl.projects.get(PROJECT_ID)

# Regex for markdown links [text](link)
link_pattern = re.compile(r'\[.*?\]\((.*?)\)')

def check_http_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        return response.status_code < 400
    except requests.RequestException:
        return False

def check_link(link, gitlab_base, group_full_path, current_file_path, repo_files):
    if link.startswith('http://') or link.startswith('https://'):
        return check_http_link(link)
    elif link.startswith('/'):
        full_url = f"{gitlab_base}{link}"
        return check_http_link(full_url)
    else:
        resolved_path = (Path(current_file_path).parent / link).resolve().as_posix()
        relative_repo_path = str(Path(resolved_path).relative_to(Path('/')))
        return relative_repo_path in repo_files

def extract_links_with_lines(text):
    lines = text.split('\n')
    results = []
    for i, line in enumerate(lines, 1):
        for match in link_pattern.finditer(line):
            results.append((i, match.group(1)))
    return results

def main():
    broken_links_report = []

    # Get compare diff between branches
    compare = project.repository_compare(MAIN_BRANCH, SOURCE_BRANCH)

    # Get full repo tree on target branch
    repo_tree = project.repository_tree(ref=SOURCE_BRANCH, all=True, recursive=True)
    repo_files = set(item['path'] for item in repo_tree)
    group_full_path = project.namespace['full_path']

    print(f"Checking diff between {MAIN_BRANCH} and {SOURCE_BRANCH}...")

    for diff in compare['diffs']:
        file_path = diff['new_path']
        if not file_path.endswith('.md'):
            continue

        print(f"Checking file: {file_path}")
        try:
            file_obj = project.files.get(file_path=file_path, ref=SOURCE_BRANCH)
            file_content = file_obj.decode().decode('utf-8')
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            continue

        links_with_lines = extract_links_with_lines(file_content)
        for line_no, link in links_with_lines:
            valid = check_link(link, GITLAB_URL, group_full_path, file_path, repo_files)
            if not valid:
                broken_links_report.append({
                    'file': file_path,
                    'line': line_no,
                    'link': link
                })

    if broken_links_report:
        print("\n=== BROKEN LINKS FOUND ===")
        for item in broken_links_report:
            print(f"{item['file']} (line {item['line']}): {item['link']}")
        print("\nMerge check failed: broken links detected.")
    else:
        print("\nNo broken links detected. Ready to merge!")

if __name__ == '__main__':
    main()
```