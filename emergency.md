Great! Here’s a modular, reusable Python system that captures terminal output, errors, and automatically creates a GitLab issue when something goes wrong.

⸻

Full Python Module: error_reporter.py

import sys
import io
import traceback
import os
import platform
import datetime
import getpass
import subprocess
import requests

class TeeLogger(io.TextIOBase):
    def __init__(self, log_path):
        self.terminal_out = sys.__stdout__
        self.terminal_err = sys.__stderr__
        self.log = open(log_path, "a")

    def write(self, message):
        self.terminal_out.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal_out.flush()
        self.log.flush()

    def close(self):
        self.log.close()

class ErrorReporter:
    def __init__(self, log_file='session.log', gitlab_token=None, project_id=None):
        self.log_file = log_file
        self.gitlab_token = gitlab_token
        self.project_id = project_id
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def start_logging(self):
        sys.stdout = sys.stderr = TeeLogger(self.log_file)

    def stop_logging(self):
        sys.stdout.log.close()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def collect_context(self, exc_info):
        sys_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Python Version": platform.python_version(),
            "User": getpass.getuser(),
            "Time (UTC)": datetime.datetime.utcnow().isoformat(),
        }

        # Optional: Git commit hash
        try:
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
            sys_info["Git Commit"] = git_hash
        except Exception:
            sys_info["Git Commit"] = "N/A"

        # Log contents
        try:
            with open(self.log_file, "r") as f:
                session_log = f.read()
        except Exception:
            session_log = "Log unavailable."

        return sys_info, session_log, exc_info

    def format_issue_body(self, sys_info, log, exc_trace):
        info_block = "\n".join(f"{k}: {v}" for k, v in sys_info.items())
        return f"""### Error Occurred

**Traceback**:

{exc_trace}

**System Info**:

{info_block}

**Session Log**:

{log[-5000:]}  # Trim to last 5000 chars if long

"""

    def create_gitlab_issue(self, title, body):
        if not self.gitlab_token or not self.project_id:
            print("Missing GitLab token or project ID.")
            return

        url = f"https://gitlab.com/api/v4/projects/{self.project_id}/issues"
        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        data = {
            "title": title,
            "description": body
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 201:
                print("GitLab issue created.")
            else:
                print("GitLab issue failed:", response.text)
        except Exception as e:
            print("Failed to report issue:", e)

    def run_with_reporting(self, func):
        self.start_logging()
        try:
            func()
        except Exception:
            exc_trace = traceback.format_exc()
            sys_info, log, exc_text = self.collect_context(exc_trace)
            issue_body = self.format_issue_body(sys_info, log, exc_text)
            self.create_gitlab_issue("Auto Error Report", issue_body)
        finally:
            self.stop_logging()


⸻

How to Use It

from error_reporter import ErrorReporter

# Setup your token/project once
reporter = ErrorReporter(
    log_file='my_session.log',
    gitlab_token='your_gitlab_token_here',
    project_id=12345678
)

def your_main_function():
    print("Doing work...")
    raise Exception("Oops! Something broke.")

reporter.run_with_reporting(your_main_function)


⸻

Next Steps

Would you like:
	•	Logging to a remote server or Slack as well?
	•	Unit test integration?
	•	Async/Thread-safe variant?

Let me know how you’d like to expand or adapt this to your environment.