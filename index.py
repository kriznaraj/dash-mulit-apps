from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app

# import server from app. Important. Do not remove.
from app import server

# Connect to your app pages
from apps import test_app3, test_app2, tpv_dashboard, app4

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Nav(
        [
            dbc.NavLink("Home", active=True, href="/"),
            dbc.NavLink("TPV Dashboard", active=True, href="/apps/tpv_dashboard"),
            # dbc.NavLink("A Test Link", disabled=True, href="/apps/test_app2"),
            # dbc.NavLink("Another Link", disabled=True, href="/apps/test_app3"),
            # dbc.NavLink("App 4", disabled=False, href="/apps/app4"),
        ], style={"background": "#ff7846"}
    ),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/tpv_dashboard':
        return tpv_dashboard.layout
    if pathname == '/apps/test_app2':
        return test_app2.layout
    if pathname == '/apps/test_app3':
        return test_app3.layout
    if pathname == '/apps/app4':
        return app4.layout
    else:
        return tpv_dashboard.layout


if __name__ == '__main__':
    app.run_server(debug=True)
