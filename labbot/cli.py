"""
formats templatable inputs
"""
from .utilities import genkwds
from functools import wraps
from jinja2 import Template
import sys


def clidec(func):
    """take potentially templateable key-words and fill with sys argv

    Parameters
    ----------
    func : function
        function to decorate

    Returns
    -------
    func : function
        decorated to handle templating
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        # compute inputs from sys argv
        form = {}
        sargs = sys.argv
        if len(sargs) > 1:
            for s in sargs[1:]:
                if "=" not in s:
                    raise ValueError("sargs contain non-keyword: %s" % s)
                k, v = s.split("=")
                form[k] = v

        func_kwds = genkwds(func, *args, **kwds)
        form = {**form, **dict(func_kwds)}

        # update kwds to reflect template
        func_kwds = {k: Template(func_kwds[k]).render(**form)
                     if isinstance(func_kwds[k], str)
                     else func_kwds[k]
                     for k in func_kwds}

        return func(**func_kwds)

    return nfunc
