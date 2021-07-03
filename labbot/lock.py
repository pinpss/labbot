"""
decorates function with locking mechanism
"""
from boltons.funcutils import wraps
import joblib
import os


def lockdec(func):
    """decorator which creates a lock for the function

    Parameters
    ----------
    func : function
        function we'd like to lock

    Returns
    -------
    func : function
        locked function
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        func_name = func.__name__
        func_hash = joblib.hash((args, kwds, func_name))
        lock_f = "{0}.lock".format(func_hash)
        if not os.path.exists(lock_f):
            open(lock_f, "w")
        else:
            print("lock file: %s for fuc: %s, \
                   nalready exists, skipping task" % (lock_f, func_name))
            return None

        try:
            res = func(*args, **kwds)
        except Exception as e:
            os.remove(lock_f)
            raise e

        os.remove(lock_f)

        return res

    return nfunc
