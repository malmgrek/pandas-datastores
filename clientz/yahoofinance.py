import requests

import attr
import pandas as pd

from clientz import Endpoint, utils


def API():
    """Yahoo! Finance

    NOTE: There are already quite good existing projects such as `yfinance`
          that solve this proble. However, some are very heavy or not
          maintained.

    Examples
    --------

    """

    session = requests.Session()

    @attr.s(frozen=True)
    class Client():

        chart = Endpoint(
            session=session,
            url="https://query1.finance.yahoo.com/v8/finance/chart/",
            tf_get_response=utils.identity,
            tf_get_resource=lambda s: s + "?",
            defaults={
                "range": "1mo",
                "period1": -2208988800,
                "period2": int(pd.Timestamp.now().timestamp()),
                "interval": "1d",
                "includePrePost": "false",
                "events": "div,splits"
            }
        )

        # TODO: Requires scraping
        financials = Endpoint(
            session=session,
            url="https://finance.yahoo.com/quote/",
        )

    return Client()
