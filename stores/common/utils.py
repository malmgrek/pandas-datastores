"""Miscellaneous utility functions

TODO: Migrate load progress and async stuff to Pandas-datastores

"""
import functools
import os
from pathlib import Path
from typing import Callable, List, Dict


def identity(x):
    return x


def curryish(f: Callable):
    """TODO Add add docstring

    """

    def g(*args, **kwargs):
        return functools.partial(f, *args, **kwargs)

    return g


def compose2(f: Callable, g: Callable):
    """Composition of two functions

    """
    def h(*args, **kwargs):
        return f(g(*args, **kwargs))

    return h


def lift(func: Callable):
    # NOTE: Could add func's *args, **kwargs here
    return lambda f: compose2(func, f)


def lift2(func: Callable):
    return (
        lambda f, g: (
            lambda *args, **kwargs: func(
                *[f(*args, **kwargs), g(*args, **kwargs)]
            )
        )
    )


def rlift(func: Callable):
    return lambda f: compose2(f, func)


def compose(*funcs: Callable):
    return functools.partial(functools.reduce, compose2)(funcs)


def pipe(arg, *funcs: Callable):
    return compose(*funcs[::-1])(arg)


listmap = curryish(compose(list, map))
tuplemap = curryish(compose(tuple, map))
listfilter = curryish(compose(list, filter))
tuplefilter = curryish(compose(tuple, filter))


def safe_type(type_class, x):
    try:
        return type_class(x)
    except ValueError:
        return None
    except TypeError:
        return None


def safe_float(x):
    return safe_type(float, x)


def safe_int(x):
    return safe_type(int, x)


# =================
# Iterable mangling
# =================


def flatten(x: List[List]):
    """Flatten a list of lists once

    """
    return functools.reduce(lambda cum, this: cum + this, x, [])


def update_dict(x: Dict, y: Dict):
    """Right-merge of two dicts

    """
    return {**x, **y}


def dissoc(x: Dict, *args):
    """New dict with the given keys removed

    """
    return {k: v for (k, v) in x.items() if k not in args}


def unpack(f: Callable):
    """Unpack arguments

    """
    def wrapped(args, **kwargs):
        return f(*args, **kwargs)

    return wrapped


def pack(f: Callable):
    """Pack arguments

    """
    def wrapped(*args, **kwargs):
        return f(args, **kwargs)

    return wrapped


# ========================
# File system side-effects
# ========================


def mkdir(filepath: str):

    Path(os.path.dirname(filepath)).mkdir(parents=True, exist_ok=True)

    def wrapper(f):
        return f

    return wrapper
