"""
decorator function to create output directories
"""
from boltons.funcutils import wraps
from .utilities import genkwds
import joblib
import json
import os


def datalocdec(func, *out_dirs):
    """creates output directories and establish link between code and dirs

    Parameters
    ----------
    func : function
        function for which we'd to create output directories
    out_dirs : tuple
        key labels for output directories in input, keys may be arg
        names as well as we combine the args and kwds into one dict
        before creating the output directories

    Returns
    -------
    func : function
        decorated to add output directories
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        t_kwds = genkwds(func, *args, **kwds)

        # store record of output directories to establish link between
        # data and code
        dataloc_dict  = {k: t_kwds[k] for k in out_dirs}
        fname = func.__name__
        mname = func.__module__
        ihash = joblib.hash((args, kwds))
        dataloc_dir = os.path.join(".dataloc", mname, fname, ihash)
        os.makedirs(dataloc_dir, exist_ok=True)
        with open(os.path.join(dataloc_dir, "out_dirs.json"), "w") as fd:
            json.dump(dataloc_dict, fd)

        # create output directories
        for k in dataloc_dict:
            os.makedirs(dataloc_dict[k], exist_ok=True)

        # run function
        return func(*args, **kwds)


    return nfunc
