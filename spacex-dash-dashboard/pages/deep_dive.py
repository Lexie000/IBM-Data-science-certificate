import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from lib.data import load_data

dash.register_page(__name__, path="/deep-dive", name="Deep Dive")

df = load_data()

launch_sites = sorted(df["LaunchSite"].dropna().unique())
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in launch_sites
]

layout = html.Div(children=[
    html.Div(className="card filter-card", children=[
        html.H2("Deep Dive", style={"marginTop": "0"}),
        html.Div(style={"display": "flex", "gap": "12px", "alignItems": "center"}, children=[
            html.Div("Launch Site:", style={"minWidth": "90px"}),
            dcc.Dropdown(
                id="dd-site",
                options=site_options,
                value="ALL",
                clearable=False,
                style={"flex": "1"},
            ),
        ]),
        html.Div(id="dd-note", className="subtle"),
    ]),

    html.Div(style={"height": "14px"}),

    html.Div(className="grid2", children=[
        html.Div(className="card", children=[dcc.Graph(id="dd-trend")]),
        html.Div(className="card", children=[dcc.Graph(id="dd-bins")]),
    ]),

    html.Div(style={"height": "14px"}),

    html.Div(className="card", children=[dcc.Graph(id="dd-map")]),
])

def site_filter(selected_site: str):
    if selected_site == "ALL":
        return df
    return df[df["LaunchSite"] == selected_site]

@dash.callback(
    Output("dd-note", "children"),
    Input("dd-site", "value"),
)
def update_note(selected_site):
    return "Tip: Use the map to spot geographic clustering; trends show month-to-month reliability changes."

@dash.callback(
    Output("dd-trend", "figure"),
    Input("dd-site", "value"),
)
def update_trend(selected_site):
    dff = site_filter(selected_site).dropna(subset=["Date"]).copy()
    dff["Month"] = dff["Date"].dt.to_period("M").dt.to_timestamp()

    # Aggregate
    trend = dff.groupby("Month").agg(
        launches=("FlightNumber", "count"),
        successes=("Class", "sum"),
    ).reset_index()

    # Raw success rate
    trend["success_rate"] = (trend["successes"] / trend["launches"]) * 100

    # Smooth (rolling window)
    window = 6  # you can try 3 or 6
    trend["roll_launches"] = trend["launches"].rolling(window, min_periods=1).sum()
    trend["roll_successes"] = trend["successes"].rolling(window, min_periods=1).sum()
    trend["success_rate_smooth"] = (trend["roll_successes"] / trend["roll_launches"]) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bars: launches
    fig.add_trace(
        go.Bar(
            x=trend["Month"],
            y=trend["launches"],
            name="Launches",
            opacity=0.85,
        ),
        secondary_y=False,
    )

    # Line: smoothed success rate
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=trend["success_rate_smooth"],
            name=f"Success Rate (rolling {window}M)",
            mode="lines+markers",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Launches per Month (bars) + Smoothed Success Rate (line)",
        margin=dict(l=20, r=20, t=60, b=20),
        bargap=0.15,
        legend_title_text="",
    )

    fig.update_xaxes(title="Month")
    fig.update_yaxes(title_text="Launches", secondary_y=False)
    fig.update_yaxes(title_text="Success Rate (%)", range=[0, 100], secondary_y=True)

    return fig

@dash.callback(
    Output("dd-bins", "figure"),
    Input("dd-site", "value"),
)
def update_bins(selected_site):
    dff = site_filter(selected_site).copy()

    # payload bins (8 bins)
    dff["PayloadBin"] = pd.qcut(dff["PayloadMass"], q=8, duplicates="drop")
    bins = dff.groupby("PayloadBin").agg(
        success_rate=("Class", "mean"),
        n=("Class", "count")
    ).reset_index()
    bins["success_rate"] = bins["success_rate"] * 100
    bins["PayloadBin"] = bins["PayloadBin"].astype(str)

    fig = px.bar(
        bins,
        x="PayloadBin",
        y="success_rate",
        hover_data=["n"],
        title="Success Rate by Payload Bin",
        labels={"PayloadBin": "Payload Range (kg)", "success_rate": "Success Rate (%)"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    fig.update_yaxes(range=[0, 100])
    return fig

@dash.callback(
    Output("dd-map", "figure"),
    Input("dd-site", "value"),
)
def update_map(selected_site):
    dff = site_filter(selected_site).dropna(subset=["Latitude", "Longitude"]).copy()

    fig = px.scatter_mapbox(
        dff,
        lat="Latitude",
        lon="Longitude",
        color="LaunchSite",
        hover_data=["Date", "BoosterVersion", "Outcome", "PayloadMass"],
        zoom=2.5,
        height=520,
        title="Launch Locations Map",
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="Launch Site",
    )
    return fig