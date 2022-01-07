import dash
import dash_bootstrap_components as dbc
import re

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                external_stylesheets=[dbc.themes.BOOTSTRAP]
                )
server = app.server


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
