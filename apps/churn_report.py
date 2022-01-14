from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from app import app
from app import convert_gsheets_url

months_dict = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9,
               'Nov': 10, 'Dec': 11}

dfv = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/1ChC2TCfCgjah9rWbA3Xg7wTy0_sCiwA6hkOETMhe36A/edit#gid=1182976160"
))

df2 = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/1ChC2TCfCgjah9rWbA3Xg7wTy0_sCiwA6hkOETMhe36A/edit#gid=16446478"
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


def add_customer_meta(c_tpv_map, df2records):
    for r in df2records:
        c = r['Name']
        if c in c_tpv_map:
            c_tpv_map[c]['Merchant Id'] = r['External Id']
            c_tpv_map[c]['Contract Value'] = r['Total Contract Amount']
    return c_tpv_map


def add_month_on_month(tpv_map, ms):
    for r in tpvMap.values():
        grn = 0
        red = 0
        for index, item in enumerate(ms):
            if index != 0:
                try:
                    p = ((r[ms[index]] - r[ms[index - 1]]) / r[ms[index]]) * 100
                    if p > 0:
                        grn += 1
                        red = 0
                    elif p < 0:
                        grn = 0
                        red += 1
                    else:
                        grn = 0
                        red = 0
                except ValueError:
                    p = 0
                    # grn = 0
                    # red = 0
                except KeyError:
                    p = 0
                    # grn = 0
                    # red = 0
                r["Growth in " + str(item)] = p
                r['color'] = 'G' if grn >= 2 else ('R' if red >= 2 else 'N')
    return tpv_map


months = dfv.month.unique()
months = sorted(months, key=lambda x: months_dict[x.split()[0]])
domains = sorted(dfv.domain.unique())
tpvMap = transform_df(dfv.to_dict('records'))
tpvMap = add_customer_meta(tpvMap, df2.to_dict('records'))
tpvMap = add_month_on_month(tpvMap, months)
tpvValues = list(tpvMap.values())
monthColumn = [{"name": i, "id": i, "type": "numeric"} for i in months]
domainColumn = [{"name": 'Domain', "id": 'domain', "type": "text"}]
merchantInfoColum = [{"name": 'Merchant Id', "id": 'Merchant Id', "type": "text"},
                     {"name": 'Contract Value', "id": 'Contract Value', "type": "numeric"}]
qoqColumns = [{"name": 'Growth in ' + str(i), "id": 'Growth in ' + str(i), "type": "numeric"} for i in months[1:-1]]
tpvColumns = domainColumn + merchantInfoColum + monthColumn + qoqColumns

# print(tpvColumns)
tpvColumnStyle = [{
    'if': {
        'column_id': i,
        'filter_query': '{{{0}}} < 10000'.format(i)
    },
    'backgroundColor': 'tomato',
    'color': 'white'
} for i in months[1:-1]]

tpvQoQColumnStyleRed = [{
    'if': {
        'column_id': 'Growth in ' + str(i),
        'filter_query': '{{Growth in {0}}} < 0'.format(i)
    },
    'backgroundColor': 'tomato',
    'color': 'white'
} for i in months[1:-1]]
tpvQoQColumnStyleGreen = [{
    'if': {
        'column_id': 'Growth in ' + str(i),
        'filter_query': '{{Growth in {0}}} > 0'.format(i)
    },
    'backgroundColor': 'green',
    'color': 'white'
} for i in months[1:-1]]

tpvColumnStyle = tpvColumnStyle + tpvQoQColumnStyleRed + tpvQoQColumnStyleGreen

tpvColFilterOptions = ['Default', 'Only QoQ Growth', 'Show All']
tpvDataFilterOptions = ['Only Red', 'Only Green', 'Show All']

layout = html.Div([
    # header
    html.Div([
        html.H3("Telescope, Magnify your customers growth!"),
        html.P("Investigate, Analyse & Predict")
    ], style={'padding': '0.5%', 'background': 'rgb(239 204 192)'}),

    # tpv table
    html.Div([
        html.Label('Early Warning Dashboard', style={"align": "left"}),
        html.Div([
            dcc.Graph(id="tpv-pie-chart",
                      figure=go.Figure(data=[go.Pie(labels=['Neutral', 'Churn', 'Pipeline'],
                                                    values=[sum(p['color'] == 'N' for p in tpvValues),
                                                            sum(p['color'] == 'R' for p in tpvValues),
                                                            sum(p['color'] == 'G' for p in tpvValues)])])),
            dbc.Row([
                dbc.Col(html.Div(dcc.Dropdown(
                    id='tpv-col-filter', value=tpvColFilterOptions[0], clearable=False,
                    options=[{'label': x, 'value': x} for x in tpvColFilterOptions]
                ))),
                dbc.Col(html.Div(dcc.Dropdown(
                    id='tpv-data-filter', value=tpvDataFilterOptions[0], clearable=False,
                    options=[{'label': x, 'value': x} for x in tpvDataFilterOptions]
                )))
            ]),
            dash_table.DataTable(
                id='tpv-tbl', data=tpvValues[:10], columns=tpvColumns,
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
                style_data_conditional=tpvColumnStyle,
                page_size=10,
                page_current=0,
                page_action='custom'
            ),
        ]),
    ], style={'padding': '1%'}),
    # tpv trend by month
    html.Div([
        html.Label('TPV Trend by Month', style={"textAlign": "left"}),
        html.Div([
            html.Div(dcc.Dropdown(
                id='customer-dropdown', value=domains[0], clearable=False,
                options=[{'label': x, 'value': x} for x in domains]
            )),
        ], className='row'),
        dcc.Graph(id='churn-bar', figure={}),
    ], style={'padding': '1%'})
])


@app.callback(
    Output(component_id='churn-bar', component_property='figure'),
    [Input(component_id='customer-dropdown', component_property='value')]
)
def display_value(customer_chosen):
    # print(customer_chosen)
    dfv_filtered = dfv[dfv['domain'] == customer_chosen]
    # print(dfv_filtered)
    # fig = px.bar(dfv_filtered, x='month', y='invoices.amount')
    fig = px.line(dfv_filtered, x='month', y='invoices.amount')
    fig = fig.update_yaxes(tickprefix="$", ticksuffix="M")
    return fig


@app.callback(
    Output('tpv-tbl', 'data'),
    Input('tpv-tbl', "page_current"),
    Input('tpv-tbl', "page_size"),
    Input('tpv-data-filter', 'value')
)
def update_table_data(page_current, page_size, data_filter):
    triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    print(triggered, page_current, page_size, data_filter)
    data = tpvValues
    if data_filter == 'Show All':
        print('all')
        data = tpvValues
    elif data_filter == 'Only Green':
        grn = list(filter(lambda a: a['color'] == 'G', tpvValues))
        print(grn)
        print('green')
        data = grn
    elif data_filter == 'Only Red':
        grn = list(filter(lambda a: a['color'] == 'R', tpvValues))
        print(grn)
        print('green')
        data = grn

    print(data[page_current * page_size:(page_current + 1) * page_size])
    return data[page_current * page_size:(page_current + 1) * page_size]


@app.callback(
    Output('tpv-tbl', 'columns'),
    Input('tpv-col-filter', 'value'),
)
def update_table_column(col_filter):
    triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    print(triggered, col_filter)
    columns = tpvColumns

    if col_filter == 'Show All':
        columns = tpvColumns
    elif col_filter == 'Only QoQ Growth':
        columns = domainColumn + qoqColumns
    elif col_filter == 'Default':
        columns = domainColumn + monthColumn + qoqColumns

    print(columns)
    return columns
