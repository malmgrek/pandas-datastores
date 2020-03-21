"""Generic utility functions"""
import functools


def curryish(f):

    def g(*args, **kwargs):
        return functools.partial(f, *args, **kwargs)

    return g


def compose2(f, g):

    def h(*args, **kwargs):
        return f(g(*args, **kwargs))

    return h


def identity(x):
    return x


def lift(func):
    # NOTE: Could add func's *args, **kwargs here
    return lambda f: compose2(func, f)


def lift2(func):
    return (
        lambda f, g: (
            lambda *args, **kwargs: func(
                *[f(*args, **kwargs), g(*args, **kwargs)]
            )
        )
    )


def rlift(func):
    return lambda f: compose2(f, func)


def compose(*funcs):
    return functools.partial(functools.reduce, compose2)(funcs)


def pipe(arg, *funcs):
    return compose(*funcs[::-1])(arg)


listmap = curryish(compose(list, map))
tuplemap = curryish(compose(tuple, map))
listfilter = curryish(compose(list, filter))
tuplefilter = curryish(compose(tuple, filter))


def maybe_to_type(type_class, x):
    try:
        return type_class(x)
    except ValueError:
        return None


maybe_to_float = lambda x: maybe_to_type(float, x)
maybe_to_int = lambda x: maybe_to_type(int, x)


def flatten(x):
    """Flatten a list of lists once

    """
    return functools.reduce(lambda cum, this: cum + this, x, [])


def update_dict(x, y):
    return {**x, **y}


def dissoc(x, *args):
    """New dict with the given keys removed

    """
    return {k: v for (k, v) in x.items() if k not in args}
