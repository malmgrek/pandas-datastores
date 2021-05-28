"""Subpages for the main Dash App

Instructions
------------

Adding new Dash app as a subpage is done by appending a new :class:`Subpage`
instance to the ``subpages`` list defined below.

"""

from typing import Callable

import dash_core_components as dcc
import dash_html_components as html

from apps import demo, hirlam


class Subpage():
    """Container for subpage information

    Parameters
    ----------

    name : str
        Human readable name of the subpage. Will be displayed in the
        front page.
    href : str
        This will constitute the endpoint where the app is found. For example
        setting the value to '/foobar' will imply that the app will be located
        at https://dash.leanheat.fi/foobar
    set_callbacks : Callable[dash.Dash, CachedDatabaseConnection]
        Mutilates the app object that is passed through different stages.
        Typically consists of callback definitions but NOTE that can
        in principle consist of any kind of mutation of app.
    Layout : Callable[CachedDatabaseConnection]
        A function that builds the html layout using database.
    description : str
        Short description of the app. Will be displayed on the front page
        boxes.

    """
    def __init__(
            self,
            name: str,
            href: str,
            set_callbacks: Callable,
            Layout: Callable,
            # preview_image: str=None,
            description: str=None
    ):
        self.name = name
        self.href = href
        self.set_callbacks = set_callbacks
        self.Layout = Layout
        self.description = description


# Add new subpages into this list
subpages = [
    Subpage(
        name="Demo app",
        href="/demo",
        set_callbacks=demo.set_callbacks,
        Layout=demo.Layout,
        description=(
            "Demo app"
        )
    ),
    Subpage(
        name="Hirlam forecasts",
        href="/hirlam",
        set_callbacks=hirlam.set_callbacks,
        Layout=hirlam.Layout,
        description=(
            "Visualize different forecasts from the HIRLAM weather model"
        )
    ),
    # ...
]


# Main page with links to subpages
index_page = html.Div(
    className="FrontPageContainer",
    children=[
        html.A(
            html.Div(
                className="Card",
                children=[
                    html.H2(x.name),
                    html.P(x.description)
                ]
            ),
            # HACK: Is it too hacky?
            href=dcc.Link(x.name, href=x.href).href,
        ) for x in subpages
    ]
)
