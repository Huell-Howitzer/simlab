Here is the full updated Dash script with:
	1.	Click-through links to open GitLab issues
	2.	Toggle to switch bubble size between Weight and Time Spent
	3.	Enhanced formatting and interactive elements

⸻

Full app.py

import os
import gitlab
import dash
import plotly.express as px
import pandas as pd
from dash import dcc, html, Input, Output

# === GitLab Config ===
GITLAB_HOST = os.getenv("GITLAB_HOST", "https://gitlab.com")
GITLAB_TOKEN = os.getenv("GITLAB_API_TOKEN")
GITLAB_GROUP_ID = int(os.getenv("GITLAB_GROUP_ID"))

# === GitLab Connection ===
gl = gitlab.Gitlab(GITLAB_HOST, private_token=GITLAB_TOKEN)

def get_all_projects(group_id):
    group = gl.groups.get(group_id)
    return group.projects.list(include_subgroups=True, all=True)

def get_all_issues(project):
    return project.issues.list(state='closed', all=True)

def collect_issues(group_id):
    records = []
    for project in get_all_projects(group_id):
        try:
            issues = get_all_issues(project)
        except gitlab.exceptions.GitlabListError:
            continue  # skip inaccessible projects

        for issue in issues:
            stats = issue.attributes.get("time_stats", {})
            spent = stats.get("total_time_spent")
            estimate = stats.get("time_estimate")
            weight = issue.attributes.get("weight")

            if spent and estimate and weight is not None:
                error = abs(spent - estimate) / max(estimate, 1)
                score = error / max(weight, 1)
                records.append({
                    "Project": project.name,
                    "Issue": issue.title,
                    "Time Spent (h)": spent / 3600,
                    "Time Estimate (h)": estimate / 3600,
                    "Weight": weight,
                    "Score": score,
                    "Web URL": issue.attributes.get("web_url"),
                })
    return pd.DataFrame(records)

# === Load Issue Data ===
df = collect_issues(GITLAB_GROUP_ID)

# === Dash App Setup ===
app = dash.Dash(__name__)
app.title = "GitLab Estimation Accuracy"

app.layout = html.Div([
    html.H1("GitLab Issue Estimate Accuracy"),
    html.Div([
        html.Label("Bubble size based on:"),
        dcc.RadioItems(
            id="bubble-size-toggle",
            options=[
                {"label": "Weight", "value": "Weight"},
                {"label": "Time Spent", "value": "Time Spent (h)"},
            ],
            value="Weight",
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        )
    ], style={"margin": "15px 0"}),

    dcc.Graph(id="bubble-chart"),

    html.Div(id="click-output", style={"margin-top": "20px", "font-weight": "bold"})
])

@app.callback(
    Output("bubble-chart", "figure"),
    Input("bubble-size-toggle", "value")
)
def update_figure(size_by):
    fig = px.scatter(
        df,
        x="Time Estimate (h)",
        y="Time Spent (h)",
        size=size_by,
        color="Score",
        hover_data=["Project", "Issue", "Score", "Weight", "Web URL"],
        title="Estimate Accuracy vs. Weight/Time",
    )
    fig.update_traces(marker=dict(opacity=0.6, line=dict(width=1, color='DarkSlateGrey')))
    return fig

@app.callback(
    Output("click-output", "children"),
    Input("bubble-chart", "clickData")
)
def display_click_data(click_data):
    if not click_data or "points" not in click_data:
        return ""
    point = click_data["points"][0]
    issue = point["customdata"][1]
    url = point["customdata"][4]
    return html.Div([
        html.Span(f"You clicked: "),
        html.A(issue, href=url, target="_blank")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)


⸻

Instructions to Run
	1.	Set these environment variables:

export GITLAB_API_TOKEN=your_token
export GITLAB_HOST=https://your.gitlab.domain
export GITLAB_GROUP_ID=123456


	2.	Install dependencies:

pip install dash plotly pandas python-gitlab


	3.	Run the app:

python app.py



⸻

Features
	•	Bubble plot visualizing estimate vs actual time
	•	Bubble size toggles between Weight and Time Spent
	•	Clicking a bubble opens the issue in GitLab
	•	Score calculation penalizes under/overestimation relative to weight

⸻

Would you like to:
	•	Cache the results?
	•	Add filters by project or label?
	•	Export results to CSV?