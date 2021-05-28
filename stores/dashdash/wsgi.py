"""WSGI server for Plotly Dash

Run as main script to start the Flask based WSGI server.

"""


from gevent.pywsgi import WSGIServer

import index
import pages


def run():
    """Run WSGI server

    """
    WSGIServer(
        ("", 8050), index.create_app(subpages=pages.subpages).server
    ).serve_forever()


if __name__ == "__main__":
    run()
