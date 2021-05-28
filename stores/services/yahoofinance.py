"""Yahoo Finance

"""
import json
import requests

import attr
import pandas as pd

from stores import Endpoint, utils


def API():
    """Yahoo! Finance

    NOTE: There are already quite good existing projects such as `yfinance`
          that solve this problem. However, some are very heavy or not
          maintained at all. Here the aim is to make as simple and clear
          tools as possible.

    Examples
    --------

    .. code-block:: python

        from stores.yahoofinance import API

        api = API()
        res = api.chart.get("MSFT")  # Microsoft

    """

    session = requests.Session()

    def extract(x: dict) -> dict:
        return (
            x
            .get("chart", {})
            .get("result", [{}])[0]
        )

    @attr.s(frozen=True)
    class Client():

        chart = Endpoint(
            session=session,
            url="https://query1.finance.yahoo.com/v8/finance/chart/",
            tf_get_response=utils.compose(
                lambda d: {
                    "meta": (
                        extract(d)
                        .get("meta", {})
                    ),
                    "quotes": pd.DataFrame(
                        index=pd.to_datetime(
                            extract(d)
                            .get("timestamp", []),
                            unit="s"
                        ),
                        data=utils.update_dict(
                            extract(d)
                            .get("indicators", {})
                            .get("quote", [[]])[0],
                            extract(d)
                            .get("indicators", {})
                            .get("adjclose", [[]])[0]
                        )
                    )
                },
                lambda res: res.json()
            ),
            tf_get_resource=lambda ticker: ticker + "?",
            defaults={
                "range": "1mo",
                "period1": -2208988800,
                "period2": int(pd.Timestamp.now().timestamp()),
                "interval": "1d",
                "includePrePost": "false",
                "events": "div,splits"
            }
        )

        # TODO: Organize the response
        financials = Endpoint(
            session=session,
            url="https://finance.yahoo.com/quote/",
            tf_get_resource=lambda ticker: ticker + "/financials",
            tf_get_response=utils.compose(
                lambda text: (
                    json
                    .loads(text)
                    .get("context")
                    .get("dispatcher")
                    .get("stores")
                    .get("QuoteSummaryStore")
                ),
                lambda res: (
                    res
                    .text
                    .split("root.App.main =")[1]
                    .split("(this)")[0]
                    .split(";\n}")[0]
                    .strip()
                )
            )
        )

        holders = Endpoint(
            session=session,
            url="https://finance.yahoo.com/quote/",
            tf_get_resource=lambda ticker: ticker + "/holders",
            tf_get_response=lambda res: pd.read_html(res.text)
        )

    return Client()
