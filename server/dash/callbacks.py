import dash
from dash.dependencies import Input, Output, State
from datetime import datetime, timezone, timedelta
import random
import plotly.graph_objects as go
from .view import create_empty_gas_smoke_graph
from ..database_module.database import *
from ..config import database
from ..config import logger

def register_callbacks(app: dash.Dash) -> None:
    @app.callback(
        [
            Output("request-status", "style"),
            Output("request-status", "children"),
            Output("detector-data-graph", "figure", allow_duplicate=True),
            Output("time-slider", "disabled", allow_duplicate=True),
            Output("date-store", "data"),
        ],
        [Input("show-data", "n_clicks")],
        [
            State("date-picker", "date"),
            State("time-slider", "value"),
            State("mac-store", "data")
         ],
        prevent_initial_call=True,
    )
    def show_data(
        n: int,
        date: str,
        time_value: list[int],
        mac_address: str
    ) -> list[dict[str, str] | str | go.Figure]:
        text = ""
        style = {}
        graph = create_empty_gas_smoke_graph()
        if date is None:
            text = "Введите дату правильно!"
            style = {
                "margin-top": "10px",
                "color": "red",
            }
            disabled = True
        else:
            dates, valueGas, valueSmoke = get_data_for_graph(date, mac_address)
            if dates is None:
                style = {
                    "margin-top": "10px",
                    "color": "red",
                }
                return style, "Данных нет", graph, True, None
            graph = add_data_graph(dates, valueGas, valueSmoke)
            
            limit = create_limit_xaxis(time_value, graph)
            graph.update_layout(xaxis=dict(range=[limit[0], limit[1]]))
            disabled = False

        return style, text, graph, disabled, date
    
    def create_scatter(dates: datetime, value: list[int], name: str, color: str) -> go.Scatter:
        return go.Scatter(
            x=dates,
            y=value,
            name=name,
            mode="lines+markers",
            marker=dict(
                size=4,
                color=color
            )
        )
    
    def add_data_graph(dates: datetime, gas: list[int], smoke: list[int]) -> go.Figure:
        graph = create_empty_gas_smoke_graph()
        scatterGas = create_scatter(dates, gas, "Gas", "Orchid")
        scatterSmoke = create_scatter(dates, smoke, "Smoke", "DarkMagenta")

        graph.add_traces([scatterGas, scatterSmoke])
        return graph
    
    def get_data_for_graph(date: str, mac_address: str) -> list[list[datetime], list[float]]:
        date_format = "%Y-%m-%d"
        date_mew = datetime.strptime(date, date_format)

        dates, valueGas, valueSmoke = [], [], []
        id_device = database.get_id_device_by_mac(mac_address)
        if id_device is not None:
            data = database.get_data_by_date(id_device, date_mew)
            if len(data) != 0:
                for d in data:
                    dates.append(d.date)
                    valueGas.append(d.gas_level)
                    valueSmoke.append(d.smoke_level)
                return dates, valueGas, valueSmoke 
            else:
                logger.warning("This device has no data.")
        else:
            logger.warning("This mac-address is not registered.")
        return None, None, None
    
    @app.callback(
        Output("detector-data-graph", "figure", allow_duplicate=True),
        Input("time-slider", "value"),
        [
            State("date-store", "data"),
            State("mac-store", "data")
        ],
        prevent_initial_call=True,
    )
    def change_xaxis(
        time_value: list[int],
        date: str,
        mac_address: str
    ) -> go.Figure:
        dates, valueGas, valueSmoke = get_data_for_graph(date, mac_address)
        graph = add_data_graph(dates, valueGas, valueSmoke)

        limit = create_limit_xaxis(time_value, graph)
        graph.update_layout(xaxis=dict(range=[limit[0], limit[1]]))
        return graph
    
    def create_limit_xaxis(time_value: list[int], graph: go.Figure) -> tuple[datetime]:
        date = graph.data[0].x[0]

        hour_start_limit = 23 if time_value[0] == 24 else time_value[0]
        minute_start_limit = 59 if time_value[0] == 24 else 0
        second_start_limit = 59 if time_value[0] == 24 else 0

        hour_end_limit = 23 if time_value[1] == 24 else time_value[1]
        minute_end_limit = 59 if time_value[1] == 24 else 0
        second_end_limit = 59 if time_value[1] == 24 else 0

        start_limit = datetime(
            date.year,
            date.month,
            date.day,
            hour=hour_start_limit,
            minute=minute_start_limit,
            second=second_start_limit,
            tzinfo=timezone.utc,
        )
        end_limit = datetime(
            date.year,
            date.month,
            date.day,
            hour=hour_end_limit,
            minute=minute_end_limit,
            second=second_end_limit,
            tzinfo=timezone.utc,
        )
        return (start_limit, end_limit)
    

    @app.callback(
        [
            Output("detector-data-graph", "figure"),
            Output("time-slider", "disabled"),
            Output("mac-store", "data"),
        ],
        [Input("url", "search")],
        [
            State("date-store", "data"),
            State("time-slider", "value"),
            State("mac-store", "data")
        ],
    )
    def update_all(
        search: str,
        date: str,
        time_value: list[int],
        mac_address: str
    ) -> list[go.Figure, bool, list[dict[str, str]]]:
        mac = search.split("=")[-1] if search else None
        if date is not None and mac_address is not None and mac_address == mac:
            dates, valueGas, valueSmoke = get_data_for_graph(date, mac_address)
            graph = add_data_graph(dates, valueGas, valueSmoke)

            limit = create_limit_xaxis(time_value, graph)
            graph.update_layout(xaxis=dict(range=[limit[0], limit[1]]))
        else:
            graph = create_empty_gas_smoke_graph()
        disabled = True if len(graph.data) == 0 else False
        return graph, disabled, mac