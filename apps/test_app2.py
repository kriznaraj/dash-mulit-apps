from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

from app import app
from app import convert_gsheets_url

dfg = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/199LeGMJNiBO_O0KaTZRYGPQrp33oBIAd23HJ0bRl7P8/edit"
))

layout = html.Div([
    html.H1('General Product Sales', style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Pre(children="Payment type", style={"fontSize": "150%"}),
            dcc.Dropdown(
                id='pymnt-dropdown', value='DEBIT', clearable=False,
                persistence=True, persistence_type='session',
                options=[{'label': x, 'value': x} for x in sorted(dfg["Type"].unique())]
            )
        ], className='six columns'),

        html.Div([
            html.Pre(children="Country of destination", style={"fontSize": "150%"}),
            dcc.Dropdown(
                id='country-dropdown', value='India', clearable=False,
                persistence=True, persistence_type='local',
                options=[{'label': x, 'value': x} for x in sorted(dfg["Order Country"].unique())]
            )
        ], className='six columns'),
    ], className='row'),

    dcc.Graph(id='my-map', figure={}),
])


@app.callback(
    Output(component_id='my-map', component_property='figure'),
    [Input(component_id='pymnt-dropdown', component_property='value'),
     Input(component_id='country-dropdown', component_property='value')]
)
def display_value(pymnt_chosen, country_chosen):
    dfg_fltrd = dfg[(dfg['Order Country'] == country_chosen) &
                    (dfg["Type"] == pymnt_chosen)]
    dfg_fltrd = dfg_fltrd.groupby(["Customer State"])[['Sales']].sum()
    dfg_fltrd.reset_index(inplace=True)
    fig = px.choropleth(dfg_fltrd, locations="Customer State",
                        locationmode="USA-states", color="Sales",
                        scope="usa")
    return fig
