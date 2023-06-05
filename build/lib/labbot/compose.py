"""
method to compose decorators
"""

def compose(*decorators):
    """produces a decorator which applies a series of decorators to a func"""

    def dec(func):

        def nfunc(*args, **kwds):

            decfunc = func

            for dec in decorators:
                decfunc = dec(decfunc)

            return decfunc(*args, **kwds)

        return nfunc

    return dec
