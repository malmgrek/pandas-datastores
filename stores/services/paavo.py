"""Statistics Finland Paavo service for demographic data

Paavo: http://pxnet2.stat.fi/PXWeb/api/v1/fi/
       Postinumeroalueittainen_avoin_tieto/

"""
import codecs
import json
import requests

import attr
import pandas as pd

from stores import Endpoint, utils
from stores.services.statfin import transform_get_response


def API():
    """Client for Paavo service for demographic data

    User interface similar to ``stores.statfin``.

    """

    session = requests.Session()

    def PaavoEndpoint(
        url,
        tf_get_response,
        tf_post_params,
        tf_post_response
    ):
        return Endpoint(
            url=(
                "http://pxnet2.stat.fi/PXWeb/api/v1/fi/"
                "Postinumeroalueittainen_avoin_tieto/" +
                url
            ),
            tf_get_response=tf_get_response,
            tf_post_params=tf_post_params,
            tf_post_response=tf_post_response,
            session=session
        )

    def tf_post_params(
        query_code="Postinumeroalue",
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
        lambda x: x.apply(pd.to_numeric, errors="coerce"),
        lambda x: x.set_index("Tiedot"),
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

        # NOTE: There are variables 1, 2, ..., 9
        #       For more information, see http://www.stat.fi/org/avoindata/
        #       paikkatietoaineistot/paavo_en.html
        #
        all_variables_2018 = PaavoEndpoint(
            url="2018/paavo_9_koko_2018.px",
            tf_get_response=transform_get_response,
            tf_post_params=tf_post_params,
            tf_post_response=tf_post_response
        )

    return Client()
