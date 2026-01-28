import dash
from dash import html, dcc


app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div(className="container", children=[
    html.Div(className="card", children=[
        html.H1("SpaceX Dashboard", className="h1"),
        html.Div(className="subtle", children=[
            dcc.Link("Overview", href="/", style={"marginRight": "14px", "color": "#4a5969ff"}),
            dcc.Link("Deep Dive", href="/deep-dive", style={"marginRight": "14px", "color": "#4a5969ff"}),
        ]),
    ]),
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)