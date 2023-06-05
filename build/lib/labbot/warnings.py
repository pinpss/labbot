"""
decorates function to suppress overly verbose warnings
"""
from boltons.funcutils import wraps
import warnings


def warndec(func):
    """suppresses warnings to reveal useful output info

    Parameters
    ----------
    func : function
        function to be decorated

    Returns
    -------
    function
        decorated to handle warnings
    """

    @wraps(func)
    def nfunc(*args, **kwds):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return func(*args, **kwds)

    return nfunc
