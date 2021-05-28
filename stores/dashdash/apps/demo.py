"""Demo app

"""


import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State


def Layout():
    return html.Div(
        className="DashboardContainer",
        children=[
            dcc.Dropdown(
                id="demo-dropdown",
                searchable=True,
                placeholder="Select value...",
                options=[
                    {
                        "label": "Rand",
                        "value": "rand"
                    },
                    {
                        "label": "Randn",
                        "value": "randn"
                    }
                ]
            ),
            dcc.Graph(
                id="demo-graph",
                className="DefaultGraph"
            )
        ]
    )


def set_callbacks(app: dash.Dash):

    @app.callback(
        Output("demo-graph", "figure"),
        [
            Input("demo-dropdown", "value")
        ]
    )
    def update_figure(name):
        fig = go.Figure()
        x = np.arange(10)
        data_generator = (
            np.random.rand if name == "rand" else
            np.random.randn if name == "randn" else
            lambda t: t
        )
        y = data_generator(10)
        fig.add_trace(go.Scatter(x=x, y=y, name=str(data_generator)))
        fig.update_layout(
            transition_duration=5,
            xaxis={
                "tickmode": "array",
                "tickvals": x,
                "ticktext": x
            },
            xaxis_title="Index",
            yaxis={"range": [-3 ,3]}
        )
        return fig

    return app
