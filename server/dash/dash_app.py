import dash
import dash_bootstrap_components as dbc
import os
from .view import create_layout
from .callbacks import register_callbacks

def create_dash_app(requests_pathname_prefix, routes_pathname_prefix):
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
    app = dash.Dash(
        __name__, 
        title="Detector Data",
        external_stylesheets=[dbc.themes.PULSE, dbc_css], 
        requests_pathname_prefix=requests_pathname_prefix,
        routes_pathname_prefix=routes_pathname_prefix,
    )
    app.layout = create_layout()

    register_callbacks(app)
    return app