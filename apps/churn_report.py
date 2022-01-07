from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

from app import app
from app import convert_gsheets_url

dfv = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/1ChC2TCfCgjah9rWbA3Xg7wTy0_sCiwA6hkOETMhe36A/edit#gid=1182976160"
))
# dfv = dfv[:100]
# print(dfv)


def transform_df(dtl):
    dt = {}
    for r in dtl:
        if r['domain'] not in dt:
            dt[r['domain']] = {'domain': r['domain'], r['month']: r['invoices.amount']}
        else:
            dt[r['domain']][r['month']] = r['invoices.amount']
    # print(dt)
    return dt


months = dfv.month.unique()
domains = sorted(dfv.domain.unique())
tpvMap = transform_df(dfv.to_dict('records'))
tpvValues = list(tpvMap.values())
# print(dfv.to_dict('records'))
# print(tpvValues)
tpvColumns = [{"name": i, "id": i, "type": "numeric"} for i in months]
# print(tpvColumns)
tpvColumns.insert(0, {"name": 'Domain', "id": 'domain', "type": "text"})
# print(tpvColumns)
tpvColumnStyle = [{
    'if': {
        'column_id': i,
        'filter_query': '{{{0}}} < 10000'.format(i)
    },
    'backgroundColor': 'tomato',
    'color': 'white'
} for i in months]
# print(tpvColumnStyle)

layout = html.Div([
    html.H3('Accounts TPV', style={"textAlign": "left"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='customer-dropdown', value=domains[0], clearable=False,
            options=[{'label': x, 'value': x} for x in domains]
        ), className='six columns'),

        # html.Div(dcc.Dropdown(
        #     id='month-dropdown', value=months[0], clearable=False,
        #     persistence=True, persistence_type='memory',
        #     options=[{'label': x, 'value': x} for x in months]
        # ), className='six columns'),
    ], className='row'),

    dcc.Graph(id='churn-bar', figure={}),

    html.H3('Early Warning Dashboard', style={"textAlign": "left"}),

    dash_table.DataTable(
        id='tpv-tbl', data=tpvValues, columns=tpvColumns,
        style_data_conditional=tpvColumnStyle
    ),
    # dbc.Alert(id='tbl_out'),
])


@app.callback(
    Output(component_id='churn-bar', component_property='figure'),
    [Input(component_id='customer-dropdown', component_property='value')]
)
def display_value(customer_chosen):
    # print(customer_chosen)
    dfv_filtered = dfv[dfv['domain'] == customer_chosen]
    # print(dfv_filtered)
    fig = px.bar(dfv_filtered, x='month', y='invoices.amount')
    fig = fig.update_yaxes(tickprefix="$", ticksuffix="M")
    return fig
