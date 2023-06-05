"""
decorates function with joblib Memory cache
"""
from functools import wraps
from joblib import Memory


def cachedec(func, location=".cache", clear=False, ignore=[]):
    """decorator which caches func

    Parameters
    ----------
    func : function
        function which we'd like to cache
    location : str
        location of cache dir
    clear : bool
        whether to clear the cache before running func
    ignore : list
        list of variables to ignore with caching

    Returns
    -------
    func : function
        decorated to handle caching
    """

    memory = Memory(location=location, verbose=False)
    if clear:
        memory.clear()

    @wraps(func)
    def nfunc(*args, **kwds):

        memfunc = memory.cache(func, ignore=ignore)
        return memfunc(*args, **kwds)

    return nfunc
