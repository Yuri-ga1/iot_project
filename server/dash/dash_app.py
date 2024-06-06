import dash
import dash_bootstrap_components as dbc
from .view import create_layout
from .callbacks import register_callbacks

def create_dash_app(requests_pathname_prefix, routes_pathname_prefix):
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.FLATLY], 
        requests_pathname_prefix=requests_pathname_prefix,
        routes_pathname_prefix=routes_pathname_prefix,
    )

    app.layout = create_layout()

    register_callbacks(app)
    return app