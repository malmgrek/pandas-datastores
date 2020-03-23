import logging
import requests

import attr

from clientz.utils import identity, update_dict


def add_params(url, **params):
    return url + (
        "" if not params else "&".join(
            "{0}={1}".format(k, v) for k, v in params.items() if v is not None
        )
    )


@attr.s(frozen=True)
class Endpoint():
    """Use to create endpoint nodes for REST API clients

    """

    # TODO: Rename functions to hooks
    url = attr.ib()
    session = attr.ib(factory=requests.Session)
    defaults = attr.ib(default={})
    headers = attr.ib(default={})
    headers_hook = attr.ib(default=identity)
    tf_url = attr.ib(default=identity)
    tf_get_params = attr.ib(default=identity)
    tf_get_response = attr.ib(default=identity)
    tf_get_resource = attr.ib(default=identity)
    tf_post_params = attr.ib(default=identity)
    tf_post_response = attr.ib(default=identity)
    timeout = attr.ib(default=10.05)

    def post(self, resource="", **params):
        url = self.url + resource
        logging.debug("POST {0}".format(url))
        r = self.session.post(
            url=url,
            json=self.tf_post_params(**params),
            headers=self.headers_hook(self.headers),
            timeout=self.timeout
        )
        r.raise_for_status()
        return self.tf_post_response(r)

    def get(self, resource="", **params):
        url = add_params(
            self.url + self.tf_get_resource(resource),
            **update_dict(self.defaults, self.tf_get_params(params))
        )
        logging.debug("GET {0}".format(url))
        r = self.session.get(
            self.tf_url(url),
            headers=self.headers_hook(self.headers),
            timeout=self.timeout
        )
        r.raise_for_status()
        return self.tf_get_response(r)
