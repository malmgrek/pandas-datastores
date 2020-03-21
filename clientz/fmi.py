import requests

import attr
import pandas as pd

from clientz import Endpoint, utils


def API():
    """Client for the Finnish Meteorological Institute weather API

    Contains two endpoints:

        * forecast_hirlam_surface_point_hourly_2d
        * historical_forecast_hirlam_surface_point_hourly_2d

    The service contains many more endpoints for Hirlam, Harmonie models,
    weather station observations etc.. Also, data can be queried in various
    formats. The present client endpoints support pointwise (latlon) queries
    of local forecasts / histories from the precalculated Hirlam model

    Parameters
    ----------

    key : str
        User key for accessing the API

    Example
    -------

    .. code-block:: python

        from clientz.fmi import API

        api = API()
        data = api.forecast_hirlam_surface_point_hourly.get(lat=60.0, lon=20.0)

    Notes
    -----

    Currently unsure whether there is a lot of historical data available
    through this service. Perhaps from other endpoints, but it seems
    that the Hirlam multi-point coverage location-wise endpoint has only
    up to past 6 hours of history available.

    """

    # TODO: beautifulsoup4 and lxml to packages.yml
    from bs4 import BeautifulSoup

    session = requests.Session()

    def WfsV2Endpoint(tf_response, url, tf_params):
        return Endpoint(
            url="https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&" + url,
            defaults={"request": "getFeature"},
            tf_get_response=tf_response,
            tf_get_params=tf_params,
            session=session
        )

    def tf_latlon(params):
        latlon = utils.compose(
            lambda x: (
                {"latlon": ",".join(utils.tuplemap(str)(x))} if all(x) else {}
            ),
            lambda x: (x.get("lat"), x.get("lon"))
        )
        return utils.pipe(
            {**params, **latlon(params)}, lambda x: utils.dissoc(x, "lat", "lon")
        )

    strip_block = utils.compose(
        utils.listmap(lambda x: x.split(" ")),
        utils.listmap(str.strip),
        lambda x: x.string.strip().splitlines()
    )

    def parse_multipointcoverage_xml(xml_string):
        soup = BeautifulSoup(xml_string, "xml")
        index = utils.pipe(
            soup.find("positions"),
            strip_block,
            utils.listmap(utils.listfilter(utils.maybe_to_int)),
            utils.listmap(lambda x: utils.maybe_to_int(x[0]) if len(x) else None),
        )
        columns = [
            tag.attrs.get("name")
            for tag in soup.find("DataRecord").find_all("field")
        ]
        data = utils.pipe(
            soup.find("DataBlock").find("doubleOrNilReasonTupleList"),
            strip_block,
            utils.listmap(utils.listmap(utils.maybe_to_float))
        )
        assert len(index) == len(data), "Index and values are incompatible"
        return (index, data, columns)

    tf_response = utils.compose(
        lambda x: pd.DataFrame(
            index=pd.to_datetime(x[0], unit="s"),
            data=x[1],
            columns=x[2]
        ),
        parse_multipointcoverage_xml,
        lambda x: x.text
    )

    @attr.s(frozen=True)
    class Client():

        forecast_hirlam_surface_point_hourly_2d = WfsV2Endpoint(
            tf_response=tf_response,
            url=(
                "storedquery_id="
                "fmi::forecast::hirlam::surface::point::multipointcoverage&"
                "timestep=60&"
                "starttime={0}&"
                "endtime={1}&"
            ).format(
                (
                    pd.Timestamp.now("UTC")
                    .floor("H")
                    .strftime('%Y-%m-%dT%H:%M:%SZ')
                ),
                (
                    (
                        pd.Timestamp.now("UTC")
                        .floor("H") + pd.Timedelta("47H")
                    )
                    .strftime('%Y-%m-%dT%H:%M:%SZ')
                )
            ),
            tf_params=tf_latlon
        )

        historical_forecast_hirlam_surface_point_hourly_2d = WfsV2Endpoint(
            tf_response=tf_response,
            url=(
                "storedquery_id="
                "fmi::forecast::hirlam::surface::point::multipointcoverage&"
                "timestep=60&"
                "starttime={0}&"
                "endtime={1}&"
            ).format(
                (
                    (
                        pd.Timestamp.now("UTC")
                        .floor("H") - pd.Timedelta("48H")
                    )
                    .strftime('%Y-%m-%dT%H:%M:%SZ')
                ),
                (
                    pd.Timestamp.now("UTC").floor("H")
                    .strftime('%Y-%m-%dT%H:%M:%SZ')
                )
            ),
            tf_params=tf_latlon
        )

    return Client()
