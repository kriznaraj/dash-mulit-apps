import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
import re
from app import app


# This function will convert the url to a download link
def convert_gsheets_url(u):
    try:
        worksheet_id = u.split("#gid=")[1]
    except:
        # Couldn't get worksheet id. Ignore it
        worksheet_id = None
    u = re.findall("https://docs.google.com/spreadsheets/d/.*?/", u)[0]
    u += "export"
    u += "?format=csv"
    if worksheet_id:
        u += "&gid={}".format(worksheet_id)
    return u


dfv = pd.read_csv(convert_gsheets_url(
    "https://docs.google.com/spreadsheets/d/1xodyyLyfhsS03KJLXvpIXZ9CgD3BjKLcqagztQD4imo/edit"
))  # GregorySmith Kaggle
sales_list = ["North American Sales", "EU Sales", "Japan Sales", "Other Sales", "World Sales"]

print(dfv)

layout = html.Div([
    html.H1('Video Games Sales', style={"textAlign": "center"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='genre-dropdown', value='Strategy', clearable=False,
            options=[{'label': x, 'value': x} for x in sorted(dfv.Genre.unique())]
        ), className='six columns'),

        html.Div(dcc.Dropdown(
            id='sales-dropdown', value='EU Sales', clearable=False,
            persistence=True, persistence_type='memory',
            options=[{'label': x, 'value': x} for x in sales_list]
        ), className='six columns'),
    ], className='row'),

    dcc.Graph(id='my-bar', figure={}),
])


@app.callback(
    Output(component_id='my-bar', component_property='figure'),
    [Input(component_id='genre-dropdown', component_property='value'),
     Input(component_id='sales-dropdown', component_property='value')]
)
def display_value(genre_chosen, sales_chosen):
    dfv_fltrd = dfv[dfv['Genre'] == genre_chosen]
    dfv_fltrd = dfv_fltrd.nlargest(10, sales_chosen)
    fig = px.bar(dfv_fltrd, x='Video Game', y=sales_chosen, color='Platform')
    fig = fig.update_yaxes(tickprefix="$", ticksuffix="M")
    return fig
