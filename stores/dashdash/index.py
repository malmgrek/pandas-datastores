"""Entry point for running the flask server

Glues together the individual Dash apps.

"""


from functools import reduce
from typing import List

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pages


def set_routes(
        app: dash.Dash,
        subpages: List[pages.Subpage],
):
    """Mutates the dash.Dash app by adding subpage routes

    Parameters
    ----------
    app : dash.Dash
        The dash application object
    subpages : List[pages.Subpages]
        List of subpage configurations

    """

    # Shove `app` through mutilations and collect layouts
    (app, layout_map) = reduce(
        lambda acc, cur: (
            cur.set_callbacks(acc[0]),
            {**acc[1], **{cur.href: cur.Layout()}}
        ),
        subpages,
        (app, {})
    )

    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(href):
        return layout_map.get(href, pages.index_page)

    return app


def create_app(subpages: List[pages.Subpage]):
    """Builds the Dash app for running.

    Parameters
    ----------
    subpages : List[pages.Subpages]
        List of subpages configurations

    """

    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        external_stylesheets=["https://codepen.io/chriddyp/bwlwgp.css"],
        # server=Flask(__name__)  # XXX: How this affects?
    )
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ])

    return set_routes(app=app, subpages=subpages)


# For launching Dash development server, run this module
# as a script
if __name__ == "__main__":
    # NOTE: It is possible that in the future we need to use an app-specific
    #       database instance (cf. China vs. Europe).
    create_app(subpages=pages.subpages).run_server(
        debug=True,
        host="127.0.0.1",
        port="8050"
    )
