import numpy as np
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

from lib.data import load_data

dash.register_page(__name__, path="/", name="Overview")

df = load_data()

min_payload = float(df["PayloadMass"].min())
max_payload = float(df["PayloadMass"].max())

launch_sites = sorted(df["LaunchSite"].dropna().unique())
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in launch_sites
]

def make_slider_marks(min_v: float, max_v: float, n: int = 5) -> dict:
    ticks = np.linspace(min_v, max_v, n)
    return {int(t): f"{int(t):,}" for t in ticks}

def filter_df(selected_site: str, payload_range: list) -> "pd.DataFrame":
    low, high = payload_range
    dff = df[(df["PayloadMass"] >= low) & (df["PayloadMass"] <= high)]
    if selected_site != "ALL":
        dff = dff[dff["LaunchSite"] == selected_site]
    return dff

layout = html.Div(children=[
    html.Div(className="kpis", children=[
        html.Div(className="kpi", children=[html.Div("Records", className="label"), html.Div(id="kpi-records", className="value")]),
        html.Div(className="kpi", children=[html.Div("Success Rate", className="label"), html.Div(id="kpi-sr", className="value")]),
        html.Div(className="kpi", children=[html.Div("Median Payload", className="label"), html.Div(id="kpi-med", className="value")]),
        html.Div(className="kpi", children=[html.Div("Selected Site", className="label"), html.Div(id="kpi-site", className="value")]),
    ]),

    html.Div(className="card filter-card", children=[
        html.Div(style={"display": "flex", "gap": "12px", "alignItems": "center"}, children=[
            html.Div("Launch Site:", style={"minWidth": "90px"}),
            dcc.Dropdown(
                id="ov-site",
                options=site_options,
                value="ALL",
                searchable=True,
                clearable=False,
                style={"flex": "1"},
            ),
        ]),
        html.Div(style={"height": "10px"}),
        html.Div("Payload Range (kg):", style={"marginBottom": "6px", "opacity": "0.85"}),
        dcc.RangeSlider(
            id="ov-payload",
            min=min_payload,
            max=max_payload,
            step=max(1, int((max_payload - min_payload) / 50)),
            value=[min_payload, max_payload],
            marks=make_slider_marks(min_payload, max_payload, n=5),
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": False},
        ),
    ]),

    html.Div(style={"height": "14px"}),

    html.Div(className="grid2", children=[
        html.Div(className="card", children=[dcc.Graph(id="ov-pie")]),
        html.Div(className="card", children=[dcc.Graph(id="ov-scatter")]),
    ]),
])

@dash.callback(
    Output("kpi-records", "children"),
    Output("kpi-sr", "children"),
    Output("kpi-med", "children"),
    Output("kpi-site", "children"),
    Input("ov-site", "value"),
    Input("ov-payload", "value"),
)
def update_kpis(selected_site, payload_range):
    dff = filter_df(selected_site, payload_range)
    n = len(dff)
    sr = (dff["Class"].mean() * 100) if n else 0
    med = float(dff["PayloadMass"].median()) if n else 0
    site_text = "ALL" if selected_site == "ALL" else selected_site
    return f"{n:,}", f"{sr:.1f}%", f"{med:,.0f}", site_text

@dash.callback(
    Output("ov-pie", "figure"),
    Input("ov-site", "value"),
    Input("ov-payload", "value"),
)
def update_pie(selected_site, payload_range):
    # Pie: ALL -> success count by site; single site -> success vs failure
    if selected_site == "ALL":
        dff = filter_df("ALL", payload_range)
        agg = dff.groupby("LaunchSite")["Class"].sum().reset_index()
        fig = px.pie(agg, values="Class", names="LaunchSite",
                     title="Total Successful Launches by Site")
    else:
        dff = filter_df(selected_site, payload_range)
        counts = dff["Class"].value_counts().rename_axis("Class").reset_index(name="count")
        counts["Outcome"] = counts["Class"].map({1: "Success", 0: "Failure"})
        fig = px.pie(counts, values="count", names="Outcome",
                     title=f"Success vs Failure — {selected_site}")
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig

@dash.callback(
    Output("ov-scatter", "figure"),
    Input("ov-site", "value"),
    Input("ov-payload", "value"),
)
def update_scatter(selected_site, payload_range):
    dff = filter_df(selected_site, payload_range).copy()

    # jitter so points aren't glued to y=0/1
    jitter = (np.random.rand(len(dff)) - 0.5) * 0.12
    dff["ClassJ"] = dff["Class"] + jitter

    fig = px.scatter(
        dff,
        x="PayloadMass",
        y="ClassJ",
        color="BoosterVersion",
        hover_data=["LaunchSite", "Orbit", "Outcome", "PayloadMass"],
        title="Payload vs Outcome",
        labels={"PayloadMass": "Payload Mass (kg)", "ClassJ": "Outcome"},
    )
    fig.update_yaxes(range=[-0.2, 1.2], tickvals=[0, 1], ticktext=["Failure (0)", "Success (1)"])
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text="Booster Version")
    return fig