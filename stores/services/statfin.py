"""Statistics Finland data service

API documentation: http://pxnet2.stat.fi/api1.html


StatFin: http://pxnet2.stat.fi/PXWeb/api/v1/fi/StatFin/

Talotyyppi | Explanation
---------------------------
         1 | One room
         2 | Two rooms
         3 | Three rooms
         4 | All apartments
         5 | All rowhouses
         6 | All

Rakennusvuosi | Explanation
---------------------------
            0 |  All
            1 | -1950
            2 |  1950
            3 |  1960
            4 |  1970
            5 |  1980
            6 |  1990
            7 |  2000
            8 |  2010
            9 |  2020


"""

import codecs
import json
import os
import requests
from time import sleep

import attr
import pandas as pd

from stores import Endpoint, utils
from stores.common.caching import (JSON, Pickle, lift, bind, Concat)


CACHE = os.path.abspath(".pandas-datastores")


def transform_get_response(res):
    raw = res.json()
    return {
        **{
            "title": raw["title"],
            "codes": [v["code"] for v in raw["variables"]]
        },
        **{
            v["code"]: {
                "text": v["text"],
                "values": v["values"],
                "valueTexts": v["valueTexts"]
            } for v in raw["variables"]
        }
    }


def API():
    """Client for StatFin data service

    Example
    -------

    .. code-block:: python

        from stores import statfin

        api = statfin.API()

        # Query data for a zip code
        res = api.apartment_prices_quarterly.post(
            query_code="Postinumero",
            query_selection_values=["00940"],
        )

        # Query metadata
        metadata = api.apartment_prices_quarterly.get()
        metadata.Postinumero.valueTexts

        # Query data for twenty zip codes using metadata
        res = api.apartment_prices_quarterly.post(
            query_code="Postinumero",
            query_selection_values=metadata.Postinumero.values[:20]
        )

    NOTE: There seems to be an issue downloading all data for all zip codes at
          once. The suggested method is to query data in chunks.

    """

    session = requests.Session()

    def ApartmentPricesEndpoint(
        url,
        tf_get_response,
        tf_post_params,
        tf_post_response
    ):
        return Endpoint(
            url="http://pxnet2.stat.fi/PXWeb/api/v1/fi/StatFin/" + url,
            tf_get_response=tf_get_response,
            tf_post_params=tf_post_params,
            tf_post_response=tf_post_response,
            session=session
        )

    def tf_post_params(
        query_code="Postinumero",
        query_selection_filter="item",
        query_selection_values=["00920"],
        response_format="json",
        **kwargs
    ):
        return utils.update_dict(
            {
                "query": [{
                    "code": query_code,
                    "selection": {
                        "filter": query_selection_filter,
                        "values": query_selection_values
                    }
                }],
                "response": {"format": response_format}
            },
            kwargs
        )

    tf_post_response = utils.compose(
        lambda x: x.apply(
            lambda s: (
                pd.to_datetime(s) if s.name.startswith("Vuosi")
                else pd.to_numeric(s, errors="coerce")
            )
        ),
        lambda x: pd.DataFrame(
            columns=[y["code"] for y in x["columns"]],
            data=[y["key"] + y["values"] for y in x["data"]]
        ),
        lambda res: json.loads(
            codecs.decode(res.content, "utf-8-sig")
        )
    )

    @attr.s(frozen=True)
    class Client():

        apartment_prices_quarterly = ApartmentPricesEndpoint(
            url="asu/ashi/nj/statfin_ashi_pxt_112p.px?",
            tf_get_response=transform_get_response,
            tf_post_params=tf_post_params,
            tf_post_response=tf_post_response
        )

        apartment_prices_yearly = ApartmentPricesEndpoint(
            url="asu/ashi/vv/statfin_ashi_pxt_112q.px?",
            tf_get_response=transform_get_response,
            tf_post_params=tf_post_params,
            tf_post_response=tf_post_response
        )

    return Client()


#
# Data sources
#
# TODO: Postinumer column to string (leading zeroes missing)
# TODO: Function to update all relevant caches
#


def YearlyMeta(filepath=os.path.join(CACHE, "yearly-meta.json")):
    """Metadata for yearly StatFin apartment prices

    TODO: What is the difference between yearly and quarterly
          metadata?

    """
    def download(api):
        return api.apartment_prices_yearly.get()

    return JSON(filepath, download)


def QuarterlyMeta(filepath=os.path.join(CACHE, "quarterly-meta.json")):
    """Metadata for quarterly StatFin apartment prices

    """
    def download(api):
        return api.apartment_prices_quarterly.get()

    return JSON(filepath, download)


def YearlyZip(zip_code):
    """Yearly apartment prices for a zip code area

    """
    filepath = os.path.join(CACHE, zip_code, "yearly.p")

    def download(api):
        sleep(0.1)
        return api.apartment_prices_yearly.post(
            query_code="Postinumero",
            query_selection_values=[zip_code]
        )

    return Pickle(filepath, download)


def QuarterlyZip(zip_code):
    """Quarterly apartment prices for a zip code area

    """
    filepath = os.path.join(CACHE, zip_code, "yearly.p")

    def download(api):
        sleep(0.1)
        return api.apartment_prices_quarterly.post(
            query_code="Postinumero",
            query_selection_values=[zip_code]
        )

    return Pickle(filepath, download)


def ConstructionYear():

    @lift
    def construction_year(meta):
        return dict(zip(
            meta["Rakennusvuosi"]["values"],
            meta["Rakennusvuosi"]["valueTexts"]
        ))

    return construction_year(YearlyMeta())


def HouseTypes():

    @lift
    def house_types(meta):
        return dict(zip(
            meta["Talotyyppi"]["values"],
            meta["Talotyyppi"]["valueTexts"]
        ))

    return house_types(YearlyMeta())


def ZipCodes():

    @lift
    def zip_codes(meta):
        return dict(zip(
            meta["Postinumero"]["values"],
            meta["Postinumero"]["valueTexts"]
        ))

    return zip_codes(YearlyMeta())


def Yearly():
    """All yearly data

    """
    @bind
    def Create(zip_codes):
        return Concat(
            utils.tuplemap(YearlyZip)(zip_codes),
            axis=0
        )

    return Create(ZipCodes())


def Quarterly():
    """All quarterly data

    """
    @bind
    def Create(zip_codes):
        return Concat(
            utils.tuplemap(QuarterlyZip)(zip_codes),
            axis=0
        )

    return Create(ZipCodes())
