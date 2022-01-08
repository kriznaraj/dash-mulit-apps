from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

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
        for index, item in enumerate(ms):
            if index != 0:
                try:
                    p = ((r[ms[index]] - r[ms[index - 1]]) / r[ms[index]]) * 100
                except ValueError:
                    p = 0
                except KeyError:
                    p = 0
                r["Month " + str(index)] = p
    return tpv_map


months = dfv.month.unique()
# months = ['August', 'September', 'October', 'November', 'December', 'January']
months = sorted(months, key=lambda x: months_dict[x.split()[0]])
domains = sorted(dfv.domain.unique())
tpvMap = transform_df(dfv.to_dict('records'))
tpvMap = add_customer_meta(tpvMap, df2.to_dict('records'))
tpvMap = add_month_on_month(tpvMap, months)
tpvValues = list(tpvMap.values())
# print(dfv.to_dict('records'))
# print(tpvValues)
tpvColumns = [{"name": i, "id": i, "type": "numeric"} for i in months]
# print(tpvColumns)
tpvColumns.insert(0, {"name": 'Domain', "id": 'domain', "type": "text"})
tpvColumns.insert(1, {"name": 'Merchant Id', "id": 'Merchant Id', "type": "text"})
tpvColumns.insert(2, {"name": 'Contract Value', "id": 'Contract Value', "type": "numeric"})

# print(tpvColumns)
tpvColumnStyle = [{
    'if': {
        'column_id': i,
        'filter_query': '{{{0}}} < 10000'.format(i)
    },
    'backgroundColor': 'tomato',
    'color': 'white'
} for i in months]
for i in range(1, len(months) - 1):
    tpvColumns.append({"name": 'Month ' + str(i), "id": 'Month ' + str(i), "type": "numeric"})
    tpvColumnStyle.append({
        'if': {
            'column_id': 'Month ' + str(i),
            'filter_query': '{{Month {0}}} < 0'.format(i)
        },
        'backgroundColor': 'tomato',
        'color': 'white'
    })
    tpvColumnStyle.append({
        'if': {
            'column_id': 'Month ' + str(i),
            'filter_query': '{{Month {0}}} > 0'.format(i)
        },
        'backgroundColor': 'green',
        'color': 'white'
    })
print(tpvColumnStyle)

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
