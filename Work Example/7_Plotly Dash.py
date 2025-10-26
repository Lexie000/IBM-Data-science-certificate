import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [
            {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'margin': '0 auto 20px'}
    ),

    # TASK 2: pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    # TASK 3: payload range slider
    html.P('Payload range (Kg):', style={'textAlign': 'center'}),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload],
        marks={0: '0', 2500: '2.5k', 5000: '5k', 7500: '7.5k', 10000: '10k'},
        tooltip={'placement': 'bottom', 'always_visible': False},
    ),

    # TASK 4: scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # 总体：按 site 聚合成功次数（class=1）
        df_agg = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_agg, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # 单一 site：显示 成功 vs 失败 计数
        dff = spacex_df[spacex_df['Launch Site'] == selected_site]
        df_count = dff['class'].value_counts().rename_axis('Outcome').reset_index(name='count')
        df_count['Outcome'] = df_count['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(df_count, values='count', names='Outcome',
                     title=f'Success vs Failure for {selected_site}')
    return fig
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    dff = spacex_df[mask]

    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Payload vs. Outcome (ALL Sites)'
               if selected_site == 'ALL'
               else f'Payload vs. Outcome ({selected_site})')
    )
    return fig
if __name__ == '__main__':
    app.run_server(debug=True)

