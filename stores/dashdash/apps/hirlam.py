"""Query data from HIRLAM forecast API

"""

from itertools import product

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

from stores import utils
from stores.services import fmi


# 'GeopHeight', 'Temperature', 'Pressure', 'Humidity', 'WindDirection',
# 'WindSpeedMS', 'WindUMS', 'WindVMS', 'MaximumWind', 'WindGust', 'DewPoint',
# 'TotalCloudCover', 'WeatherSymbol3', 'LowCloudCover', 'MediumCloudCover',
# 'HighCloudCover', 'Precipitation1h', 'PrecipitationAmount',
# 'RadiationGlobalAccumulation', 'RadiationLWAccumulation',
# 'RadiationNetSurfaceLWAccumulation', 'RadiationNetSurfaceSWAccumulation',
# 'RadiationDiffuseAccumulation', 'LandSeaMask'

# TODO: Let user select which columns to use from tickbocks -> dynamically
# create the number of subplots


dimensions = [
    "Temperature",
    "Pressure",
    "Humidity",
    "WindSpeedMS",
    "MaximumWind",
    "PrecipitationAmount",
    "RadiationGlobalAccumulation",
    "TotalCloudCover",
    "GeopHeight"
]
ncols = int(len(dimensions) ** 0.5)


def Layout():
    return html.Div(
        className="DashboardContainer",
        style={"max-width": "2000px"},
        children=[
            html.Div(
                children=[
                    dcc.Input(
                        id="lat",
                        type="number",
                        placeholder="latitude",
                        debounce=True,
                        value=60.1699
                    ),
                    dcc.Input(
                        id="lon",
                        type="number",
                        placeholder="longitude",
                        debounce=True,
                        value=24.9384
                    ),
                ]
            ),
            dcc.Graph(
                id="graph",
                className="DefaultGraph",
            )
        ]
    )


def set_callbacks(app: dash.Dash):

    @app.callback(
        Output("graph", "figure"),
        [
            Input("lat", "value"),
            Input("lon", "value")
        ]
    )
    def update_figure(lat, lon):

        fig = make_subplots(
            rows=ncols,
            cols=ncols
        )

        if lat is None or lon is None:
            return fig

        api = fmi.API()
        data = api.forecast_hirlam_surface_point_hourly_2d.get(
            lat=lat, lon=lon
        )
        rowcols = utils.pipe(
            range(1, ncols + 1),
            lambda x: list(product(x, x))
        )
        for (dim, (row, col)) in zip(dimensions, rowcols):
            fig.add_trace(
                go.Scatter(x=data.index, y=data[dim], name=dim),
                row=row,
                col=col,
            )
            fig.update_yaxes(title_text=dim, row=row, col=col)

        fig.update_layout(
            height=1000,
            width=2000,
            title_text="FMI | HIRLAM | forecasts",
            showlegend=False
        )

        return fig

    return app
