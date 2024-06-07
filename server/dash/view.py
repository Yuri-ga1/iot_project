import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
import datetime 

def create_layout() -> html.Div:
    layout = html.Div(
        [
            dcc.Store(id="mac-store", storage_type="session"),
            dcc.Store(id="date-store", storage_type="session"),
            dcc.Location(id="url", refresh=False),
            dbc.Row(
                html.H3("Displaying Detector Data"),
                style={"margin-top": "20px"}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select date:", style={"font-size": "18px", "margin-right": "10px"}),
                            dcc.DatePickerSingle(
                                id='date-picker',
                                max_date_allowed=datetime.datetime.now(),
                                display_format="YYYY-MM-DD",
                                placeholder="YYYY-MM-DD",
                                date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                persistence=True,
                                persistence_type="session",
                                className="dbc",
                                style={"border": "1px solid Thistle"}
                            )
                        ],
                        width="auto",
                        style={"display": "flex", "align-items": "center"}
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Show",
                            id="show-data",
                            style={"border-radius": "7px", "font-size": "18px"}
                        ),
                        width="auto",
                        style={"display": "flex", "align-items": "center"}
                    ),
                ],
                style={"margin-top": "20px"}
            ),
            dbc.Row(
                html.Div("", id="request-status")
            ),
            dbc.Row(
                dcc.Graph(
                    id='detector-data-graph',
                    figure=create_empty_gas_smoke_graph()
                ),
            ),
            dbc.Row(
                [
                    html.Div("Select time:", style={"font-size": "18px"}),
                    html.Div(
                        create_time_slider(),
                        style={"margin-top": "20px"}
                    ),
                ]
            )    
        ],
        style={"margin-right": "30px", "margin-left": "30px"}
    )
    return layout

def create_empty_gas_smoke_graph() -> go.Figure:
    graph = go.Figure()

    graph.update_layout(
        title_font=dict(size=24, color="black"),
        plot_bgcolor="white",
        margin=dict(l=0, t=30, r=0, b=0),
        xaxis=dict(
            title="Time",
            gridcolor="#E1E2E2",
            linecolor="black",
            showline=True,
            mirror=True,
        ),
        yaxis=dict(
            title="Data",
            gridcolor="#E1E2E2",
            linecolor="black",
            showline=True,
            mirror=True,
        ),
    )

    return graph

def create_time_slider() -> dcc.RangeSlider:
    marks = {i: f"{i:02d}:00" if i % 3 == 0 else "" for i in range(25)}
    time_slider = dcc.RangeSlider(
        id="time-slider",
        min=0,
        max=24,
        step=1,
        marks=marks,
        value=[0, 24],
        allowCross=False,
        tooltip={
            "placement": "top",
            "style": {"fontSize": "18px"},
            "template": "{value}:00",
        },
        disabled=True,
        persistence=True,
        persistence_type="session",
        className="dbc"
    )
    return time_slider
