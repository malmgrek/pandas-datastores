"""Data caching in file system

"""
import json
import pickle
from typing import Callable, Iterable

import attr
import pandas as pd

from clientz.common import utils


@attr.s(frozen=True)
class Source():
    """Generic data source

    """

    # Download data from a remote location
    download = attr.ib()

    # Load data from disk cache
    load = attr.ib()

    # Download with saving
    update = attr.ib()


def Landfill(
        filepath: str,
        download: Callable,
        dump: Callable,
        load: Callable
):
    """Dump load source

    """
    @utils.mkdir(filepath)
    def update(api):
        return dump(download(api), filepath)

    return Source(
        download=download,
        load=lambda: load(filepath),
        update=update
    )


def Pickle(filepath: str, download: Callable):
    """Landfill of pickle

    """
    def dump(data, path):
        pickle.dump(data, open(path, "wb+"))
        return data

    def load(path):
        return pickle.load(open(path, "rb"))

    return Landfill(filepath, download, dump, load)


def JSON(filepath: str, download: Callable):
    """Landfill of json

    """
    def dump(data, path):
        json.dump(data, open(path, "w+"))
        return data

    def load(path):
        return json.load(open(path, "r"))

    return Landfill(filepath, download, dump, load)


def HDF5(filepath: str, download: Callable):
    """Landfill of hdf5

    """
    def dump(data, path):
        # TODO
        return

    def load(path):
        # TODO
        return

    return Landfill(filepath, download, dump, load)


def lift(func: Callable):
    """Lift a function

    lift :: (a -> b) -> Source(a) -> Source(b)

    Example
    -------

    ..code-block :: python

        triple = lift(lambda x: 3 * x)
        Tripled = triple(Source)

    """
    def lifted(*sources: Source):

        return Source(
            download=lambda api: func(
                *utils.tuplemap(lambda x: x.download(api))(sources)
            ),
            load=lambda: func(
                *utils.tuplemap(lambda x: x.load())(sources)
            ),
            update=lambda api: func(
                *utils.tuplemap(lambda x: x.update(api))(sources)
            )
        )

    return lifted


def bind(func: Callable):
    """Bind a function which returns a data source

    """
    def bound(*sources: Source):
        return Source(
            # FIXME: Unnecessary lambda definition?
            download=lambda api: func(
                *utils.tuplemap(lambda x: x.download(api))(sources)
            ).download(api),
            load=lambda: func(
                *utils.tuplemap(lambda x: x.load())(sources)
            ).load(),
            update=lambda api: func(
                *utils.tuplemap(lambda x: x.update(api))(sources)
            ).update(api)
        )

    return bound


def Concat(sources: Iterable[Source], **kwargs):
    """Concatenate an iterable of sources

    """

    @lift
    def concat(*frames: pd.DataFrame, **kwargs):
        return pd.concat(frames, **kwargs)

    return concat(*sources)
