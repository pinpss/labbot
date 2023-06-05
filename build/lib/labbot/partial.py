"""
method for creating new decorator which applies all inputs except func
"""


def dpart(decorator, *args, **kwds):
    """applies reverse functools.partial, add arg to beginning"""

    def dec(func):

        return decorator(func, *args, **kwds)

    dec.decorator = decorator
    dec.args = args
    dec.kwds = kwds

    return dec
