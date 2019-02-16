
"""
TODO
"""


def named_partial(func, *args, **kwargs):
    from functools import partial
    ret = partial(func, *args, **kwargs)
    ret.__name__ = func.__name__
    return ret


def xy_data_generator(func, div=1):
    from itertools import count
    for i in count():
        x = i / div
        yield x, func(x)
