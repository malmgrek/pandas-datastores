"""Inderes

"""
import json
import logging
import os
import requests
from requests.utils import requote_uri

import attr
import numpy as np
import pandas as pd
from user_agent import generate_user_agent

from clientz import Endpoint, utils


def here(*args):
    return os.path.join(
        os.path.dirname(__file__), *args
    )


# Company ISIN codes
ARGS_0 = [
    "FI0009010912", "FI4000008719", "FI0009014351", "FI0009014377",
    "FI0009005961", "FI0009013296", "FI0009005987", "FI0009004824",
    "FI4000074984", "FI0009002422", "FI0009800643", "FI0009010862",
    "FI0009007132", "FI0009008072", "FI0009008403", "FI0009013429",
    "FI0009007884", "SE0000667925", "FI0009007991", "FI4000062781",
    "FI0009000665", "FI0009000459", "FI0009004741", "FI4000043435",
    "FI4000369657", "FI4000415252", "FI0009007637", "FI0009007264",
    "FI0009008650", "FI0009000681", "FI0009000277", "FI0009013403",
    "FI0009005870", "FI0009007835", "FI0009014575", "FI0009005078",
    "FI0009003727", "FI4000049812", "FI0009009377", "FI4000062195",
    "FI0009000400", "FI0009000202", "FI0009005318", "FI0009007355",
    "FI0009003305", "FI0009007694", "FI4000369947", "FI4000349113",
    "FI0009003503", "FI4000064332", "FI0009008387", "FI4000081427",
    "FI0009008080", "FI0009800379", "FI4000029905", "FI4000115464",
    "FI4000153580", "FI0009900385", "FI0009015309", "FI0009009617",
    "FI0009003230", "FI4000092556", "FI0009015580", "FI4000123070",
    "FI0009900559", "FI0009007660", "FI4000153515", "FI0009007728",
    "FI0009900708", "FI0009900682", "FI4000178256", "FI4000185533",
    "FI4000127527", "FI0009013114", "FI0009800296", "FI0009007306",
    "FI4000048418", "FI4000198031", "FI4000232913", "FI4000251897",
    "FI4000233267", "SE0008294334", "FI0009006407", "FI0009900237",
    "FI4000081138", "FI0009900187", "FI0009008452", "FI4000206750",
    "FI0009900468", "FI4000058870", "FI0009008924", "FI0009007983",
    "FI0009008270", "FI0009801310", "FI4000170915", "FI4000092523",
    "FI4000157441", "FI4000270350", "FI4000252127", "FI4000283130",
    "FI4000282868", "FI4000251830", "FI4000306873", "FI4000301585",
    "FI4000322326", "EE3100004466", "FI4000348974", "FI4000349212",
    "FI4000348909", "FI4000364120", "FI4000369608", "FI4000391487",
    "FI4000400262", "FI4000414800"
]


# NOTE: These are now hard-coded in the method
ARGS_1 = ["0", "2020", "2021"]


def API():
    """Client for downloading data in the Inderes table

    Main endpoints:

        * data_table -- Stock price table
          -> ``get`` returns ``pd.DataFrame``.
        * company_forecast -- Some fundamentals, forecasts and recommendations
          -> ``get`` returns ``dict``.

    Example
    -------

    .. code-block :: python

        from clientz.inderes import API

        api = API()
        table = api.data_table.get()
        forecast = api.company_forecast.get()

        # P/E ratios
        pe = calculate_pe(y=forecast["this"], t=table)

        # P/B ratios
        pb = calculate_pb(y=forecast["this"], t=table)

        # Dividend yield
        div_yield = calculate_div_yield(y=forecast["this"], t=table)

    TODO: Example on how to retrieve the most important fundamentals

    """

    session = requests.Session()

    with open(here("data", "isin.json"), "r") as f:
        isin = json.load(f)

    def headers_hook(*args, **kwargs):
        """Randomize user agent

        """
        return {
            "User-Agent": generate_user_agent()
        }

    def tf_company_response(res):

        get_meta = utils.compose(
            lambda x: pd.DataFrame(
                index=[isin.get(v["isin"]) for v in x],
                data=[
                    {
                        "target_price": np.float(v.get("target_price", "NaN")),
                        "suositus": v.get("suositus"),
                        "isin": v.get("isin")
                    } for v in x
                ]
            ),
            utils.listfilter(lambda x: x["year"] == "0")
        )

        def create_get_year(year):
            return utils.compose(
                lambda x: pd.DataFrame(
                    index=[isin.get(v["isin"]) for v in x],
                    data=[
                        utils.dissoc(v, "target_price", "suositus", "isin")
                        for v in x
                    ]
                ).astype(float),
                utils.listfilter(lambda x: x["year"] == year)
            )

        get_this = create_get_year(ARGS_1[1])
        get_next = create_get_year(ARGS_1[2])

        return utils.pipe(
            res.json(),
            lambda x: {
                "meta": get_meta(x),
                "this": get_this(x),
                "next": get_next(x)
            }
        )

    @attr.s(frozen=True)
    class Client():

        company_forecast = Endpoint(
            session=session,
            url=(
                "https://www.inderes.fi/fi/"
                "rest/views/inderes_numbers_only_year_data.json?"
            ),
            headers_hook=headers_hook,
            defaults={
                "args_0": ",".join(ARGS_0),
                "args_1": ",".join(ARGS_1)
            },
            tf_url=utils.compose(
                requote_uri,
                lambda url: (
                    url
                    .replace("args_0", "args[0]")
                    .replace("args_1", "args[1]")
                )
            ),
            tf_get_response=tf_company_response
        )

        raw_json = Endpoint(
            session=session,
            url="https://www.inderes.fi/fi/osakevertailu",
            headers_hook=headers_hook,
            tf_get_response=utils.compose(
                lambda d: (
                    d
                    .get("inderes_ranking")
                    .get("company_gathered_data")
                ),
                json.loads,
                lambda res: (
                    res
                    .text
                    .split("Drupal.settings,")[1]
                    .split(");")[0]
                    .strip()
                )
            )
        )

        data_table = Endpoint(
            session=session,
            url="https://www.inderes.fi/fi/osakevertailu",
            headers_hook=headers_hook,
            tf_get_response=utils.compose(
                lambda data: data.astype({
                    'diff1d': float,
                    'diff1dprc': float,
                    'bidprice': float,
                    'askprice': float,
                    'lastprice': float,
                    'dayhighprice': float,
                    'daylowprice': float,
                    'closeprice1d': float,
                    'turnover': float,
                    'quantity': float,
                    'timestamp': float,
                    'this_month_millistream': float,
                }),
                lambda x: pd.DataFrame(
                    index=[isin.get(v["isin"]) for v in x],
                    data=x
                ),
                lambda d: list(d.values()),
                lambda d: (
                    d
                    .get("inderes_ranking")
                    .get("company_gathered_data")
                ),
                json.loads,
                lambda res: (
                    res
                    .text
                    .split("Drupal.settings,")[1]
                    .split(");")[0]
                    .strip()
                )
            )
        )

    return Client()


#
# Tools for using the data
#


def update_isin_lookup():
    """Fetch (ISIN, company_name) pairs

    """
    with open(here("data", "isin.json"), "w+") as f:
        json.dump(
            utils.pipe(
                API().raw_json.get(),
                lambda table: {
                    isin: table.get(isin).get("company_name")
                    for isin in sorted(list(table.keys()))
                }
            ),
            f
        )

    logging.info("Updated ISIN lookup")


def no_of_shares(y: pd.DataFrame) -> pd.Series:
    """Number of shares per company

    Parameters
    ----------
    y: Company forecast for a given year

    """
    return y["no_of_shares_k_year_end"].add(y["no_of_shares_a_year_end"])


def calculate_pb(y: pd.DataFrame, t: pd.DataFrame) -> pd.Series:
    """Price to book ratio per company

    Parameters
    ----------
    y: Company forecast for a given year
    t: Data table

    """
    index = y.index.intersection(t.index)
    y = y.loc[index]
    t = t.loc[index]
    return t["lastprice"].div(y["bv"]).mul(no_of_shares(y))


def calculate_pe(y: pd.DataFrame, t: pd.DataFrame)-> pd.Series:
    """Price to earnings ratio per company

    Parameters
    ----------
    y: Company forecast for a year
    t: Data table

    """
    index = y.index.intersection(t.index)
    y = y.loc[index]
    t = t.loc[index]
    return t["lastprice"].div(y["net_earnings"]).mul(no_of_shares(y))


def calculate_div_yield(y: pd.DataFrame, t: pd.DataFrame) -> pd.Series:
    """Divided yield per company

    Parameters
    ----------
    y: Company forecast for a year
    t: Data table
    """
    index = y.index.intersection(t.index)
    y = y.loc[index]
    t = t.loc[index]
    return y["diva"].div(t["lastprice"])
