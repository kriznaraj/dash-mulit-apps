import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from app import convert_gsheets_url

dfv = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/1ChC2TCfCgjah9rWbA3Xg7wTy0_sCiwA6hkOETMhe36A/edit#gid=1666733709"
))

dfv = dfv[:100]

ticket_records = dfv.to_dict('records')
print(ticket_records)

cols = ["Priority", "Ticket ID", "Ticket Descr", "Module", "SLA Breach", "Sentiment", "Internal Status", "Created on",
        "TTR", "External Status", "POC", "Tags"]
ticketsColumn = [{"name": i, "id": i, "type": "text"} for i in cols]
ticketsColumnStyle = [{
    'if': {
        'column_id': 'SLA Breach',
        'filter_query': '{SLA Breach} = "Y"'
    },
    'backgroundColor': 'tomato',
    'color': 'white'
}, {
    'if': {
        'column_id': 'SLA Breach',
        'filter_query': '{SLA Breach} = "N"'
    },
    'backgroundColor': 'green',
    'color': 'white'
}, {
    'if': {
        'column_id': 'Sentiment',
        'filter_query': '{Sentiment} = "Unhappy"'
    },
    'backgroundColor': 'tomato',
    'color': 'white'
}, {
    'if': {
        'column_id': 'Sentiment',
        'filter_query': '{Sentiment} = "Satisfied"'
    },
    'backgroundColor': 'green',
    'color': 'white'
}]


def tickets_by_module():
    mp = {
        'Integration': [0, 1, 0, 0, 0, 0],
        'Payments': [0, 0, 0, 0, 0, 2],
        'Login': [0, 0, 1, 0, 0, 0]
    }
    month = ["Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]

    fig = go.Figure()
    # Create and style traces
    for k in mp:
        fig.add_trace(go.Scatter(x=month, y=mp[k], name=k))
    fig.update_layout(title='Tickets by Month and Module',
                      xaxis_title='Month',
                      yaxis_title='Tickets Count')
    return fig


def tickets_by_priority():
    mp = {
        '0.6': [0, 1, 0, 0, 0, 0],
        '0.4': [0, 0, 0, 0, 0, 2],
        '0.9': [0, 0, 1, 0, 0, 0]
    }
    month = ["Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]

    fig = go.Figure()
    # Create and style traces
    for k in mp:
        fig.add_trace(go.Scatter(x=month, y=mp[k], name=k))
    fig.update_layout(title='Tickets by Month and Priority',
                      xaxis_title='Month',
                      yaxis_title='Tickets Count')
    return fig


layout = html.Div([
    # header
    html.Div([
        html.H3("Telescope, Magnify your customers growth!"),
        html.P("Investigate, Analyse & Predict")
    ], style={'padding': '0.5%', 'background': 'rgb(239 204 192)'}),

    # tpv table
    html.Div([
        html.Div([

            dbc.Row([
                dbc.Col([html.Label('Tickets Details - (Account Name)')]),
            ]),

            dbc.Row([
                dash_table.DataTable(
                    id='tickets-tbl', data=ticket_records[:10], columns=ticketsColumn,
                    # filter_action='native',
                    column_selectable="single",
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0
                    },
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': 'rgb(210, 210, 210)',
                        'color': 'black',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=ticketsColumnStyle,
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    page_size=10,
                    page_current=0,
                    page_action='custom'
                )
            ]),
        ]),
    ], style={'padding': '1%'}),
    # tickets trend by month
    html.Div([
        dbc.Row([
            dbc.Col([html.Label('Tickets Trend - Module vs Month')]),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(id='tickets-by-module', figure=tickets_by_module())),
                 dbc.Col(dcc.Graph(id='tickets-by-priority', figure=tickets_by_priority()))]),
    ], style={'padding': '1%'})

])


@app.callback(
    Output('tickets-tbl', 'data'),
    Input('tickets-tbl', "page_current"),
    Input('tickets-tbl', "page_size")
)
def update_table_data(page_current, page_size):
    triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    print(triggered, page_current, page_size)
    data = ticket_records
    return data[page_current * page_size:(page_current + 1) * page_size]
