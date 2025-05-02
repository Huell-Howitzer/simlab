Here’s a Python script that:
	1.	Uses requests to get issues under a GitLab epic.
	2.	Calculates total estimated time and time spent.
	3.	Builds a Gantt chart using plotly with progress bars representing completion.

⸻

Python Script

import requests
import datetime
import plotly.express as px

# --- Configuration ---
GITLAB_URL = "https://gitlab.example.com"  # Replace with your GitLab instance
PRIVATE_TOKEN = "your_private_token"       # Replace with your private token
EPIC_ID = 123                              # Replace with your Epic ID
GROUP_ID = 456                             # Replace with your Group ID

HEADERS = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

# --- Helper Functions ---
def get_epic_issues(group_id, epic_id):
    url = f"{GITLAB_URL}/api/v4/groups/{group_id}/epics/{epic_id}/issues"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_issue_details(project_id, issue_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues/{issue_iid}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# --- Main Logic ---
issues = get_epic_issues(GROUP_ID, EPIC_ID)
gantt_data = []

for issue in issues:
    issue_detail = get_issue_details(issue['project_id'], issue['iid'])

    title = issue_detail['title']
    created_at = issue_detail['created_at']
    due_date = issue_detail.get('due_date') or datetime.datetime.utcnow().date().isoformat()
    time_estimate = issue_detail['time_stats']['time_estimate']  # in seconds
    time_spent = issue_detail['time_stats']['total_time_spent']  # in seconds

    percent_complete = (
        (time_spent / time_estimate) * 100 if time_estimate > 0 else 0
    )

    gantt_data.append({
        "Task": title,
        "Start": created_at,
        "Finish": due_date,
        "Percent Complete": percent_complete,
    })

# --- Plot Gantt Chart ---
fig = px.timeline(
    gantt_data,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Percent Complete",
    title="Epic Issue Progress (Gantt Chart)",
    labels={"Percent Complete": "Progress (%)"},
)

fig.update_yaxes(autorange="reversed")  # Gantt style
fig.update_layout(xaxis_title="Date", yaxis_title="Issues", coloraxis_colorbar_title="% Complete")
fig.show()



⸻

Notes:
	•	created_at and due_date are used as start and finish times. If a due date isn’t set, today’s date is used as a fallback.
	•	The progress bar coloring reflects the percent complete.
	•	If you want a stacked overall progress bar too, I can extend the script to compute and plot that separately.

Would you like to also show overall progress for the entire epic as a percentage?

---

Great — for an air-gapped GitLab environment, you’ll want to:
	1.	Use only internal URLs.
	2.	Avoid any external internet requests, including Plotly’s default cloud rendering.
	3.	Save the Gantt chart as a self-contained HTML file (or as an image if using kaleido or orca offline).
	4.	Make sure dependencies are installed offline, e.g., using a wheelhouse or manually downloaded packages.

⸻

Air-Gapped-Compatible Version

This version:
	•	Uses plotly.offline to avoid internet access.
	•	Writes the chart to a local .html file you can open in any browser.

import requests
import datetime
import plotly.express as px
import pandas as pd
import plotly.io as pio
from plotly.offline import plot

# --- Configuration ---
GITLAB_URL = "http://gitlab.local"  # Use your internal GitLab hostname/IP
PRIVATE_TOKEN = "your_private_token"
EPIC_ID = 123
GROUP_ID = 456

HEADERS = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

# --- Helper Functions ---
def get_epic_issues(group_id, epic_id):
    url = f"{GITLAB_URL}/api/v4/groups/{group_id}/epics/{epic_id}/issues"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_issue_details(project_id, issue_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues/{issue_iid}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# --- Main Logic ---
issues = get_epic_issues(GROUP_ID, EPIC_ID)
gantt_data = []

total_time_estimate = 0
total_time_spent = 0

for issue in issues:
    issue_detail = get_issue_details(issue['project_id'], issue['iid'])

    title = issue_detail['title']
    created_at = issue_detail['created_at']
    due_date = issue_detail.get('due_date') or datetime.datetime.utcnow().date().isoformat()
    time_estimate = issue_detail['time_stats']['time_estimate']
    time_spent = issue_detail['time_stats']['total_time_spent']

    percent_complete = (
        (time_spent / time_estimate) * 100 if time_estimate > 0 else 0
    )

    total_time_estimate += time_estimate
    total_time_spent += time_spent

    gantt_data.append({
        "Task": title,
        "Start": created_at,
        "Finish": due_date,
        "Percent Complete": percent_complete,
    })

# --- Overall Progress ---
overall_percent_complete = (
    (total_time_spent / total_time_estimate) * 100 if total_time_estimate > 0 else 0
)

gantt_data.append({
    "Task": f"Overall Progress ({overall_percent_complete:.1f}%)",
    "Start": min(d['Start'] for d in gantt_data),
    "Finish": max(d['Finish'] for d in gantt_data),
    "Percent Complete": overall_percent_complete,
})

# --- Plot Gantt Chart Offline ---
df = pd.DataFrame(gantt_data)
fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Percent Complete",
    title="Epic Issue Progress (Offline Gantt Chart)",
    labels={"Percent Complete": "Progress (%)"},
)

fig.update_yaxes(autorange="reversed")
fig.update_layout(xaxis_title="Date", yaxis_title="Issues", coloraxis_colorbar_title="% Complete")

# Save as standalone HTML (works in air-gapped browsers)
plot(fig, filename="epic_gantt_chart.html", auto_open=False)



⸻

Offline Requirements

Make sure you’ve pre-installed:

pip install plotly pandas requests

If fully offline, download wheels from PyPI and transfer them via USB/CD/etc.

⸻

Would you also like:
	•	PNG or PDF export instead of HTML?
	•	A CLI tool version (e.g., python epic_gantt.py --epic 123 --group 456)?
	•	Or integration into your GitLab documentation system?

Let me know how else to tailor it.

---

Awesome — if you already have a function that aggregates all issues across your GitLab group hierarchy, you can build powerful visualizations on top of that. Below are 5 cool, useful visualizations you can generate with plotly, pandas, and optionally networkx.

⸻

1. Sunburst Chart: Work Distribution by Group → Project → Label

Shows how work is organized and tagged at multiple levels.

import plotly.express as px

df = pd.DataFrame(all_issues)  # Your aggregated issue data

fig = px.sunburst(
    df,
    path=["group", "project", "labels"],  # Must be normalized per issue
    values="weight",  # or use 1 per issue, or time estimate/spent
    title="Work Distribution: Group → Project → Label"
)
fig.show()



⸻

2. Treemap: Issues by Assignee and Label

Compact view to show who has what kind of work.

fig = px.treemap(
    df,
    path=["assignee", "labels"],
    values="weight",  # or time_spent
    title="Issue Load per Assignee by Label"
)
fig.show()



⸻

3. Timeline: Milestones Over Time

Visualize when milestones are planned or due.

milestones_df = pd.DataFrame(all_milestones)  # Must include start/due dates

fig = px.timeline(
    milestones_df,
    x_start="start_date",
    x_end="due_date",
    y="title",
    color="group",  # Or by status
    title="Milestone Timeline by Group"
)
fig.update_yaxes(autorange="reversed")
fig.show()



⸻

4. Bubble Chart: Issue Time Estimate vs Spent (with Label Coloring)

Helps identify under/over-estimated issues.

fig = px.scatter(
    df,
    x="time_estimate",
    y="time_spent",
    size="weight",
    color="labels",
    hover_name="title",
    title="Time Estimate vs Time Spent per Issue"
)
fig.show()



⸻

5. Network Graph: Epics, Issues, and Blocking Dependencies

Build a directed graph to show issue relationships.

import networkx as nx
import plotly.graph_objects as go

G = nx.DiGraph()

# Add nodes and edges
for issue in all_issues:
    G.add_node(issue["id"], label=issue["title"])
    for blocked in issue.get("blocked_by", []):
        G.add_edge(blocked, issue["id"])

# Plot layout
pos = nx.spring_layout(G)
edge_x, edge_y, node_x, node_y, labels = [], [], [], [], []

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    labels.append(G.nodes[node]['label'])

fig = go.Figure(
    data=[
        go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1), hoverinfo='none'),
        go.Scatter(x=node_x, y=node_y, mode='markers+text', text=labels,
                   marker=dict(size=10), textposition="bottom center")
    ],
    layout=go.Layout(
        title="Issue Dependency Network",
        showlegend=False,
        hovermode='closest'
    )
)
fig.show()



⸻

Ideas for Extensions
	•	Heatmap of issues opened vs closed over time (date histogram).
	•	Stacked bar chart: issues by status across projects.
	•	Radar chart of team members’ time spent per label.
	•	Sankey diagram: Issue → Assignee → Milestone → Epic.

⸻

Would you like me to package these into a reusable CLI tool or dashboard template?


---


Awesome — let’s expand your GitLab visualization toolkit with 5 more advanced and insightful charts, assuming you’re working with a structured list of issues and related metadata.

⸻

6. Heatmap: Issues Created vs Closed by Week

Tracks project activity trends.

df["created_week"] = pd.to_datetime(df["created_at"]).dt.to_period("W").astype(str)
df["closed_week"] = pd.to_datetime(df["closed_at"]).dt.to_period("W").astype(str)

created_heatmap = df.groupby("created_week").size().reset_index(name="created_count")
closed_heatmap = df.groupby("closed_week").size().reset_index(name="closed_count")

timeline = pd.merge(created_heatmap, closed_heatmap, left_on="created_week", right_on="closed_week", how="outer").fillna(0)
timeline["week"] = timeline["created_week"].combine_first(timeline["closed_week"])
timeline = timeline[["week", "created_count", "closed_count"]]

fig = px.bar(timeline, x="week", y=["created_count", "closed_count"], barmode="group",
             title="Issue Creation vs Closure Weekly")
fig.show()



⸻

7. Parallel Coordinates Plot: Effort Profile

Compares issues across multiple dimensions — label count, weight, time estimate, and time spent.

df["label_count"] = df["labels"].apply(lambda x: len(x) if x else 0)

fig = px.parallel_coordinates(
    df,
    dimensions=["label_count", "weight", "time_estimate", "time_spent"],
    color="time_spent",
    title="Effort Profiles Across Issues"
)
fig.show()



⸻

8. Donut Chart: Workload by Milestone or Epic

Aesthetically shows distribution of issue weight or time.

df_milestone = df[df["milestone"].notnull()]
fig = px.pie(
    df_milestone,
    names="milestone",
    values="weight",  # or "time_estimate"
    hole=0.4,
    title="Workload by Milestone"
)
fig.show()



⸻

9. Radar Chart: Assignee Skill/Focus Profile

Visualize what type of work each person is doing (by label or issue type).

from plotly.subplots import make_subplots
import plotly.graph_objects as go

label_set = sorted({label for labels in df["labels"] if labels for label in labels})
assignee_groups = df.groupby("assignee")

radar_data = []
for assignee, group in assignee_groups:
    label_counts = {label: 0 for label in label_set}
    for labels in group["labels"]:
        if labels:
            for label in labels:
                label_counts[label] += 1
    radar_data.append(go.Scatterpolar(
        r=list(label_counts.values()),
        theta=label_set,
        fill='toself',
        name=assignee or "Unassigned"
    ))

fig = go.Figure(radar_data)
fig.update_layout(title="Assignee Work Profile by Label", polar=dict(radialaxis=dict(visible=True)))
fig.show()



⸻

10. Sankey Diagram: Epic → Milestone → Label Flow

Tracks how work flows across multiple dimensions.

import plotly.graph_objects as go

source_labels = []
target_labels = []
values = []

def add_flow(source_col, target_col):
    source_target_pairs = df[[source_col, target_col]].dropna()
    group = source_target_pairs.groupby([source_col, target_col]).size().reset_index(name='count')
    for _, row in group.iterrows():
        source = row[source_col]
        target = row[target_col]
        if source not in source_labels:
            source_labels.append(source)
        if target not in target_labels:
            target_labels.append(target)
        values.append(row['count'])

add_flow("epic", "milestone")
add_flow("milestone", "labels")  # Assumes one label per row for simplicity

all_labels = list(dict.fromkeys(source_labels + target_labels))  # Preserve order

link_sources = [all_labels.index(s) for s in source_labels]
link_targets = [all_labels.index(t) for t in target_labels]

fig = go.Figure(data=[go.Sankey(
    node=dict(label=all_labels),
    link=dict(source=link_sources, target=link_targets, value=values)
)])
fig.update_layout(title="Epic → Milestone → Label Flow")
fig.show()



⸻

What You Could Do Next
	•	Wrap this into a dashboard: Flask + Dash or Streamlit = simple GUI.
	•	Generate static reports: plotly.io.write_html, PDF, or kaleido export.
	•	Trigger visuals nightly via cron/GitLab CI if connected.
	•	Drilldown: Filter plots interactively per project/assignee/milestone.

⸻

Would you like a visualize.py CLI tool that lets you pass arguments like --by assignee, --output html, or --include-closed?


---

Perfect — let’s build a Flask + Dash app that works in an air-gapped environment and visualizes your GitLab data with the charts we’ve discussed.

⸻

Project Overview
	•	app.py: Flask app hosting the Dash dashboard
	•	dash_app/: Dash layout + logic
	•	data_loader.py: Your existing GitLab data function
	•	Assumes you already have a function like get_all_issues() that returns issues across all projects

⸻

Step-by-Step Setup

1. File: app.py (Flask + Dash integration)

from flask import Flask
from dash_app.layout import init_dashboard

server = Flask(__name__)
app = init_dashboard(server)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)



⸻

2. File: dash_app/layout.py

from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
from data_loader import get_all_issues

def init_dashboard(server):
    app = Dash(__name__, server=server, routes_pathname_prefix="/dashboard/")

    issues = get_all_issues()
    df = pd.DataFrame(issues)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])
    df["week"] = df["created_at"].dt.to_period("W").astype(str)

    # --- Gantt ---
    df["percent_complete"] = df.apply(
        lambda row: (row["time_spent"] / row["time_estimate"]) * 100 if row["time_estimate"] else 0, axis=1
    )
    gantt_fig = px.timeline(
        df,
        x_start="created_at",
        x_end="closed_at",
        y="title",
        color="percent_complete",
        title="Gantt Chart: Time Estimate vs Actual",
    )
    gantt_fig.update_yaxes(autorange="reversed")

    # --- Weekly Trend ---
    trend_df = df.groupby("week").size().reset_index(name="count")
    trend_fig = px.bar(trend_df, x="week", y="count", title="Issues Created per Week")

    # --- Treemap ---
    df["label"] = df["labels"].apply(lambda x: x[0] if x else "Unlabeled")
    tree_fig = px.treemap(df, path=["assignee", "label"], values="weight", title="Workload by Assignee")

    app.layout = html.Div([
        html.H1("GitLab Project Dashboard"),
        dcc.Graph(figure=gantt_fig),
        dcc.Graph(figure=trend_fig),
        dcc.Graph(figure=tree_fig),
    ])

    return app



⸻

3. File: data_loader.py

Replace this stub with your existing function:

def get_all_issues():
    # Replace this with your real logic.
    return [
        {
            "title": "Issue 1",
            "created_at": "2024-12-01",
            "closed_at": "2024-12-10",
            "labels": ["bug"],
            "assignee": "alice",
            "weight": 2,
            "time_estimate": 3600,
            "time_spent": 1800,
        },
        # ...
    ]



⸻

4. Install (Offline if Needed)

Prepare a wheelhouse ahead of time, or install normally:

pip install flask dash pandas plotly



⸻

5. Run It

python app.py

Visit: http://localhost:8050/dashboard/

⸻

Next Features You Can Add
	•	Filters (dropdown for project, assignee, label)
	•	Export buttons (HTML, CSV)
	•	Tabs for different types of charts
	•	Epics, milestones, and blockers as subplots or layers

⸻

Would you like me to generate a full working zip of this, or add filtering widgets next?


---


Great — let’s add interactive widgets (dropdowns, multi-selects, and tabs) to your Dash dashboard so users can:
	•	Filter by Assignee
	•	Filter by Label
	•	Choose which chart to view (Gantt, Treemap, Weekly Trend)

⸻

Updated layout.py with Widgets and Tabs

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from data_loader import get_all_issues

def init_dashboard(server):
    app = Dash(__name__, server=server, routes_pathname_prefix="/dashboard/")

    issues = get_all_issues()
    df = pd.DataFrame(issues)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])
    df["week"] = df["created_at"].dt.to_period("W").astype(str)
    df["label"] = df["labels"].apply(lambda x: x[0] if x else "Unlabeled")
    df["assignee"] = df["assignee"].fillna("Unassigned")
    df["percent_complete"] = df.apply(
        lambda row: (row["time_spent"] / row["time_estimate"]) * 100 if row["time_estimate"] else 0, axis=1
    )

    assignees = sorted(df["assignee"].unique())
    labels = sorted(df["label"].unique())

    app.layout = html.Div([
        html.H1("GitLab Issue Dashboard"),
        html.Div([
            html.Label("Filter by Assignee:"),
            dcc.Dropdown(
                options=[{"label": a, "value": a} for a in assignees],
                value=assignees,
                multi=True,
                id="assignee-filter"
            ),
            html.Label("Filter by Label:"),
            dcc.Dropdown(
                options=[{"label": l, "value": l} for l in labels],
                value=labels,
                multi=True,
                id="label-filter"
            ),
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),

        dcc.Tabs(id="chart-tabs", value="gantt", children=[
            dcc.Tab(label="Gantt Chart", value="gantt"),
            dcc.Tab(label="Weekly Trend", value="trend"),
            dcc.Tab(label="Treemap", value="treemap"),
        ]),

        dcc.Graph(id="chart-output")
    ])

    @app.callback(
        Output("chart-output", "figure"),
        Input("chart-tabs", "value"),
        Input("assignee-filter", "value"),
        Input("label-filter", "value"),
    )
    def update_chart(tab, selected_assignees, selected_labels):
        filtered = df[df["assignee"].isin(selected_assignees) & df["label"].isin(selected_labels)]

        if tab == "gantt":
            fig = px.timeline(
                filtered,
                x_start="created_at",
                x_end="closed_at",
                y="title",
                color="percent_complete",
                title="Gantt Chart: Time Estimate vs Actual",
            )
            fig.update_yaxes(autorange="reversed")
        elif tab == "trend":
            trend_df = filtered.groupby("week").size().reset_index(name="count")
            fig = px.bar(trend_df, x="week", y="count", title="Issues Created per Week")
        elif tab == "treemap":
            fig = px.treemap(filtered, path=["assignee", "label"], values="weight", title="Workload by Assignee")
        else:
            fig = px.scatter(title="Invalid Tab")

        return fig

    return app



⸻

What This Adds:
	•	Dropdowns to filter by:
	•	Assignee
	•	Label (first label only for simplicity)
	•	Tabs to switch between:
	•	Gantt Chart
	•	Weekly Trend
	•	Treemap

⸻

Next Ideas?
	•	Add date range pickers
	•	Let user select multiple labels per issue
	•	Display epic and milestone progress
	•	Add export to HTML/CSV buttons

Would you like me to add download/export buttons or support for filtering by date ranges or milestones next?

---

Perfect — let’s implement the first three enhancements:
	1.	Date Range Picker to filter by issue creation date
	2.	Support for multiple labels per issue (instead of only the first label)
	3.	Epic and Milestone Progress Tracking, shown as charts

⸻

Updated layout.py With All 3 Features

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from data_loader import get_all_issues

def init_dashboard(server):
    app = Dash(__name__, server=server, routes_pathname_prefix="/dashboard/")

    issues = get_all_issues()
    df = pd.DataFrame(issues)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])
    df["week"] = df["created_at"].dt.to_period("W").astype(str)
    df["assignee"] = df["assignee"].fillna("Unassigned")
    df["milestone"] = df["milestone"].fillna("None")
    df["epic"] = df["epic"].fillna("None")

    # Handle multi-labels: explode into rows
    df["labels"] = df["labels"].apply(lambda x: x if isinstance(x, list) else [])
    exploded_df = df.explode("labels")
    exploded_df["label"] = exploded_df["labels"].fillna("Unlabeled")

    # Calculate percent complete
    df["percent_complete"] = df.apply(
        lambda row: (row["time_spent"] / row["time_estimate"]) * 100 if row["time_estimate"] else 0, axis=1
    )

    assignees = sorted(df["assignee"].unique())
    all_labels = sorted(exploded_df["label"].unique())
    min_date, max_date = df["created_at"].min(), df["created_at"].max()

    app.layout = html.Div([
        html.H1("GitLab Issue Dashboard"),

        html.Div([
            html.Label("Filter by Assignee:"),
            dcc.Dropdown(
                options=[{"label": a, "value": a} for a in assignees],
                value=assignees,
                multi=True,
                id="assignee-filter"
            ),
            html.Label("Filter by Label:"),
            dcc.Dropdown(
                options=[{"label": l, "value": l} for l in all_labels],
                value=all_labels,
                multi=True,
                id="label-filter"
            ),
            html.Label("Filter by Date Range:"),
            dcc.DatePickerRange(
                id="date-range",
                start_date=min_date,
                end_date=max_date,
                display_format="YYYY-MM-DD",
            )
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),

        dcc.Tabs(id="chart-tabs", value="gantt", children=[
            dcc.Tab(label="Gantt Chart", value="gantt"),
            dcc.Tab(label="Weekly Trend", value="trend"),
            dcc.Tab(label="Treemap", value="treemap"),
            dcc.Tab(label="Epic Progress", value="epic"),
            dcc.Tab(label="Milestone Progress", value="milestone"),
        ]),

        dcc.Graph(id="chart-output")
    ])

    @app.callback(
        Output("chart-output", "figure"),
        Input("chart-tabs", "value"),
        Input("assignee-filter", "value"),
        Input("label-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    )
    def update_chart(tab, selected_assignees, selected_labels, start_date, end_date):
        filtered = exploded_df[
            (exploded_df["assignee"].isin(selected_assignees)) &
            (exploded_df["label"].isin(selected_labels)) &
            (exploded_df["created_at"] >= pd.to_datetime(start_date)) &
            (exploded_df["created_at"] <= pd.to_datetime(end_date))
        ]

        if tab == "gantt":
            fig = px.timeline(
                filtered,
                x_start="created_at",
                x_end="closed_at",
                y="title",
                color="percent_complete",
                title="Gantt Chart: Time Estimate vs Actual"
            )
            fig.update_yaxes(autorange="reversed")

        elif tab == "trend":
            trend_df = filtered.groupby("week").size().reset_index(name="count")
            fig = px.bar(trend_df, x="week", y="count", title="Issues Created per Week")

        elif tab == "treemap":
            fig = px.treemap(filtered, path=["assignee", "label"], values="weight", title="Workload by Assignee")

        elif tab == "epic":
            epic_df = df[
                (df["assignee"].isin(selected_assignees)) &
                (df["created_at"] >= pd.to_datetime(start_date)) &
                (df["created_at"] <= pd.to_datetime(end_date))
            ]
            epic_grouped = epic_df.groupby("epic").agg({
                "time_estimate": "sum",
                "time_spent": "sum"
            }).reset_index()
            epic_grouped["percent_complete"] = (epic_grouped["time_spent"] / epic_grouped["time_estimate"]) * 100
            fig = px.bar(epic_grouped, x="epic", y="percent_complete", title="Epic Completion %")

        elif tab == "milestone":
            ms_df = df[
                (df["assignee"].isin(selected_assignees)) &
                (df["created_at"] >= pd.to_datetime(start_date)) &
                (df["created_at"] <= pd.to_datetime(end_date))
            ]
            ms_grouped = ms_df.groupby("milestone").agg({
                "time_estimate": "sum",
                "time_spent": "sum"
            }).reset_index()
            ms_grouped["percent_complete"] = (ms_grouped["time_spent"] / ms_grouped["time_estimate"]) * 100
            fig = px.bar(ms_grouped, x="milestone", y="percent_complete", title="Milestone Completion %")

        else:
            fig = px.scatter(title="Invalid Tab")

        return fig

    return app



⸻

What You Get Now:
	•	Date range filtering on issue creation date
	•	True multi-label support (exploded rows)
	•	New tabs for:
	•	Epic progress (time_spent / time_estimate)
	•	Milestone progress (time_spent / time_estimate)

⸻

Would you like to:
	•	Add CSV or image export buttons?
	•	Integrate this into a scheduled PDF/email report?
	•	Support more advanced filters like milestone state or blocked issues?

Let me know how you’d like to evolve this further!

---
Awesome — let’s level up your dashboard with more powerful filters, allowing fine-grained control across issue state, milestone, epic, and blocking status.

⸻

New Filters to Add:
	1.	Issue State: opened, closed, all
	2.	Milestone Selector
	3.	Epic Selector
	4.	Blocked/Blocking/Unlinked Issues Only (if you include that in your data)

⸻

1. Update Layout: Add Filter Widgets

Inside your layout’s filter html.Div, add these:

html.Label("Filter by Issue State:"),
dcc.RadioItems(
    id="state-filter",
    options=[
        {"label": "Open", "value": "opened"},
        {"label": "Closed", "value": "closed"},
        {"label": "All", "value": "all"}
    ],
    value="all",
    labelStyle={"display": "inline-block", "margin-right": "10px"}
),

html.Label("Filter by Milestone:"),
dcc.Dropdown(
    id="milestone-filter",
    options=[{"label": m, "value": m} for m in sorted(df["milestone"].unique())],
    value=sorted(df["milestone"].unique()),
    multi=True
),

html.Label("Filter by Epic:"),
dcc.Dropdown(
    id="epic-filter",
    options=[{"label": e, "value": e} for e in sorted(df["epic"].unique())],
    value=sorted(df["epic"].unique()),
    multi=True
),

html.Label("Blocked Status:"),
dcc.RadioItems(
    id="blocked-filter",
    options=[
        {"label": "All", "value": "all"},
        {"label": "Only Blocked", "value": "blocked"},
        {"label": "Only Blocking", "value": "blocking"},
        {"label": "Unlinked Only", "value": "unlinked"}
    ],
    value="all",
    labelStyle={"display": "inline-block", "margin-right": "10px"}
),



⸻

2. Update Callback Inputs

Extend your @app.callback inputs:

Input("state-filter", "value"),
Input("milestone-filter", "value"),
Input("epic-filter", "value"),
Input("blocked-filter", "value"),



⸻

3. Update Filtering Logic

Extend your update_chart function with new filtering rules:

def update_chart(tab, assignees, labels, start_date, end_date,
                 state, milestones, epics, blocked_mode):

    filtered = exploded_df[
        (exploded_df["assignee"].isin(assignees)) &
        (exploded_df["label"].isin(labels)) &
        (exploded_df["created_at"] >= pd.to_datetime(start_date)) &
        (exploded_df["created_at"] <= pd.to_datetime(end_date)) &
        (exploded_df["milestone"].isin(milestones)) &
        (exploded_df["epic"].isin(epics))
    ]

    if state != "all":
        filtered = filtered[filtered["state"] == state]

    if blocked_mode == "blocked":
        filtered = filtered[filtered["is_blocked"] == True]
    elif blocked_mode == "blocking":
        filtered = filtered[filtered["is_blocking"] == True]
    elif blocked_mode == "unlinked":
        filtered = filtered[
            (~filtered["is_blocked"]) & (~filtered["is_blocking"])
        ]

Make sure your get_all_issues() returns state, is_blocked, and is_blocking fields per issue — you can compute these using GitLab’s related issues API.

⸻

Optional UX Enhancements
	•	Label search filter: Add searchable=True to dcc.Dropdown
	•	Select all toggle for long lists (can be done with a callback)
	•	“Reset filters” button to clear selections

⸻

Would you like help updating get_all_issues() to support blocked status and GitLab’s related issues API?

---

Great! Here’s how to update your get_all_issues() function to include:
	•	state: "opened" or "closed"
	•	is_blocked: whether this issue is blocked by other issues
	•	is_blocking: whether this issue blocks other issues

⸻

1. GitLab API Endpoints Used

To get blocking relationships:

GET /projects/:id/issues/:issue_iid/links

It returns relationships with link_type = "blocks" or "is_blocked_by".

⸻

2. Updated get_all_issues() Skeleton

import requests

GITLAB_URL = "https://gitlab.example.com"
PRIVATE_TOKEN = "your_private_token"
HEADERS = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def get_all_issues():
    all_issues = []

    # Example group/project traversal — adapt this to your structure
    group_id = 123  # your top-level group ID
    projects = get_all_projects_in_group(group_id)

    for project in projects:
        project_id = project["id"]
        issues = get_project_issues(project_id)

        for issue in issues:
            issue_data = {
                "project_id": project_id,
                "iid": issue["iid"],
                "title": issue["title"],
                "assignee": issue["assignee"]["name"] if issue["assignee"] else "Unassigned",
                "labels": issue["labels"],
                "milestone": issue["milestone"]["title"] if issue["milestone"] else "None",
                "epic": issue.get("epic", {}).get("title", "None"),  # if using epic API
                "weight": issue.get("weight", 1),
                "time_estimate": issue["time_stats"]["time_estimate"],
                "time_spent": issue["time_stats"]["total_time_spent"],
                "created_at": issue["created_at"],
                "closed_at": issue["closed_at"],
                "state": issue["state"],  # opened or closed
            }

            # Fetch related issues to check for blocked/blocking
            links = get_issue_links(project_id, issue["iid"])
            issue_data["is_blocked"] = any(l["link_type"] == "is_blocked_by" for l in links)
            issue_data["is_blocking"] = any(l["link_type"] == "blocks" for l in links)

            all_issues.append(issue_data)

    return all_issues

def get_all_projects_in_group(group_id):
    url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects?include_subgroups=true&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_project_issues(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues?scope=all&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_issue_links(project_id, issue_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues/{issue_iid}/links"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        return []  # Links not supported
    response.raise_for_status()
    return response.json()



⸻

3. Performance Tips for Air-Gapped GitLab
	•	GitLab rate-limits API calls — use pagination (X-Next-Page) if you expect lots of issues.
	•	Consider caching links for issues you’ve already queried.
	•	If slow, run the script once a day and store the data in a .json or .parquet file for the dashboard to use.

⸻

Would you like a version of this that caches API responses, or uses parallel requests to speed it up?

---

Awesome — here’s how to integrate these 5 new visualizations into your Flask + Dash app.

⸻

Step 1: Add Tabs to Your Layout

In your existing layout.py, extend the dcc.Tabs component:

dcc.Tabs(id="chart-tabs", value="gantt", children=[
    dcc.Tab(label="Gantt Chart", value="gantt"),
    dcc.Tab(label="Weekly Trend", value="trend"),
    dcc.Tab(label="Treemap", value="treemap"),
    dcc.Tab(label="Epic Progress", value="epic"),
    dcc.Tab(label="Milestone Progress", value="milestone"),
    dcc.Tab(label="Cumulative Flow", value="cfd"),
    dcc.Tab(label="Burnup by Assignee", value="burnup"),
    dcc.Tab(label="Issue Age Distribution", value="age"),
    dcc.Tab(label="Status Donut", value="donut"),
    dcc.Tab(label="Box Plot: Time by Label", value="box"),
    dcc.Tab(label="Heatmap: Assignee × Milestone", value="heatmap"),
]),



⸻

Step 2: Extend the Callback

Inside the same update_chart callback, add new chart logic for each of the new tabs:

elif tab == "cfd":
    df["created_week"] = df["created_at"].dt.to_period("W").astype(str)
    df["closed_week"] = df["closed_at"].dt.to_period("W").astype(str)
    created = df.groupby("created_week").size().rename("Created")
    closed = df.groupby("closed_week").size().rename("Closed")
    timeline = pd.concat([created, closed], axis=1).fillna(0).cumsum().reset_index().rename(columns={"index": "Week"})
    timeline["In Progress"] = timeline["Created"] - timeline["Closed"]
    fig = px.area(timeline, x="Week", y=["Created", "In Progress", "Closed"],
                  title="Cumulative Flow Diagram", labels={"value": "Issue Count", "variable": "State"})

elif tab == "burnup":
    df["closed_week"] = df["closed_at"].dt.to_period("W").astype(str)
    burn_df = df[df["state"] == "closed"].groupby(["closed_week", "assignee"]).size().reset_index(name="closed")
    fig = px.line(burn_df, x="closed_week", y="closed", color="assignee",
                  title="Issues Closed Over Time (Burnup by Assignee)")

elif tab == "age":
    age_df = df[df["state"] == "closed"].copy()
    age_df["age_days"] = (age_df["closed_at"] - age_df["created_at"]).dt.days
    fig = px.histogram(age_df, x="age_days", nbins=20,
                       title="Issue Age Distribution (Days Until Closed)", labels={"age_days": "Days Open"})

elif tab == "donut":
    open_count = len(df[df["state"] == "opened"])
    closed_count = len(df[df["state"] == "closed"])
    blocked_count = len(df[df["is_blocked"] == True])
    fig = go.Figure(data=[go.Pie(
        labels=["Open", "Closed", "Blocked"],
        values=[open_count, closed_count, blocked_count],
        hole=0.5
    )])
    fig.update_layout(title="Open vs Closed vs Blocked Issues")

elif tab == "box":
    exploded = df.explode("labels")
    exploded = exploded[exploded["time_spent"] > 0]
    fig = px.box(
        exploded, x="labels", y="time_spent",
        title="Time Spent per Label (Box Plot)",
        labels={"time_spent": "Time Spent (sec)"},
        points="all"
    )

elif tab == "heatmap":
    pivot = df.pivot_table(index="assignee", columns="milestone", values="title", aggfunc="count", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, title="Issue Count: Assignee vs Milestone",
                    labels=dict(x="Milestone", y="Assignee", color="Issue Count"))



⸻

Step 3: Requirements Reminder

Make sure these are in your environment:

pip install pandas plotly dash



⸻

Optional Next Enhancements
	•	Add download/export (CSV, PNG)
	•	Add notifications (e.g. “milestone overdue”)
	•	Serve multiple dashboards on different URLs
	•	Bundle into a .whl or container image for team use

Would you like me to generate a dashboard skeleton repo zip file or help you modularize the plots into reusable components?

---

Perfect — since you can’t distribute a container, the best approach is to distribute your Flask + Dash GitLab visualizer as a self-contained Python app, like this:

⸻

Recommended Structure

gitlab_dashboard/
├── app.py                 # Launches the Flask + Dash app
├── dash_app/
│   ├── __init__.py
│   └── layout.py          # Dash layout, tabs, callbacks
├── data_loader.py         # GitLab API fetching logic
├── requirements.txt       # Dependencies
├── README.md              # How to install and run



⸻

1. How to Distribute It

Distribute the app via:
	•	A .zip or .tar.gz file of the above directory
	•	Place it on your GitLab instance or file share
	•	Ensure team members have Python 3.8+ and can run:

pip install -r requirements.txt
python app.py

You can also provide a simple setup script if needed.

⸻

2. requirements.txt Example

flask
dash
pandas
plotly
requests

You can pre-download these as .whl files in a vendor/ folder if fully air-gapped.

⸻

3. README.md Example

# GitLab Dashboard

A Flask + Dash application for visualizing GitLab data across groups and projects.

## Setup

1. Install Python 3.8+
2. Create a virtual environment (optional)
3. Install dependencies:

```bash
pip install -r requirements.txt

	4.	Run the app:

python app.py

	5.	Open your browser to http://localhost:8050/dashboard/

Notes
	•	Works offline / air-gapped
	•	Requires access to GitLab API and a private token
	•	You can configure the group ID and token inside data_loader.py

---

## **Want It Even Smoother?**

I can provide:

- A `run.sh` script that bootstraps everything
- A `config.py` file for token and base URL
- Optional local `.json` cache files for teams who can’t hit GitLab directly

Would you like me to package this structure and zip it for you, or help add config and cache support next?

---

To create a desktop shortcut to launch your Flask + Dash app (on Linux, Windows, or macOS), you’ll want to create a launcher that opens a terminal and runs python app.py in the app’s directory.

⸻

1. On Linux (GNOME, KDE, etc.)

Create a .desktop file:

[Desktop Entry]
Name=GitLab Dashboard
Comment=Launch Flask + Dash GitLab Visualizer
Exec=/usr/bin/gnome-terminal -- bash -c "cd /path/to/gitlab_dashboard && python app.py; exec bash"
Icon=/path/to/icon.png
Terminal=false
Type=Application
Categories=Development;

Steps:
	1.	Save this as gitlab-dashboard.desktop
	2.	Make it executable:

chmod +x gitlab-dashboard.desktop


	3.	Move it to your desktop or applications folder:

mv gitlab-dashboard.desktop ~/Desktop/



Replace /path/to/gitlab_dashboard with the full path, and adjust gnome-terminal if using konsole, xterm, etc.

⸻

2. On Windows

Option 1: Batch Script + Shortcut
	1.	Create run_dashboard.bat:

@echo off
cd /d C:\Path\To\gitlab_dashboard
python app.py
pause

	2.	Create a shortcut to the .bat file:
	•	Right-click > Create Shortcut
	•	Optionally change icon

⸻

Option 2: Python shortcut directly

Use a tool like pyshortcuts:

pip install pyshortcuts

from pyshortcuts import make_shortcut

make_shortcut(
    script="python app.py",
    name="GitLab Dashboard",
    icon="/path/to/icon.ico",
    startmenu=True,
    desktop=True
)



⸻

3. On macOS

Use Automator or .command file:
	1.	Create a file like run_dashboard.command:

#!/bin/bash
cd /Users/you/gitlab_dashboard
source venv/bin/activate  # if you use a virtual environment
python app.py

	2.	Make it executable:

chmod +x run_dashboard.command

	3.	Drag it to the Dock or Desktop.

⸻

Optional: Add Custom Icon
	•	Use .png or .ico icons
	•	Set them via Icon= on Linux .desktop or shortcut properties in Windows

⸻

Would you like a cross-platform installer script or a .command / .desktop file generator?