from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app

# import server from app. Important. Do not remove.
from app import server

# Connect to your app pages
from apps import test_app3, test_app2, churn_report

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Nav(
        [
            dbc.NavLink("Churn Report", active=True, href="/apps/churn_report"),
            dbc.NavLink("A Test Link", disabled=True, href="/apps/test_app2"),
            dbc.NavLink("Another Link", disabled=True, href="/apps/test_app3"),
        ]
    ),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/churn_report':
        return churn_report.layout
    if pathname == '/apps/test_app2':
        return test_app2.layout
    if pathname == '/apps/test_app3':
        return test_app3.layout
    else:
        return churn_report.layout


if __name__ == '__main__':
    app.run_server(debug=False)
