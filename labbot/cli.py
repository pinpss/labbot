"""
formats templatable inputs
"""
from .utilities import genkwds
from functools import wraps
from jinja2 import Template
import ast
import sys


def clidec(func):
    """pass command line arguments into function

    Additionally handles possible arguments that are only passed to template

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
        nkwds = {}
        key = None
        sargs = sys.argv
        if len(sargs) > 1:
            for s in sargs[1:]:
                if s[:2] == "--":
                    key = s[2:]
                    nkwds[key] = []
                elif key is None:
                    raise ValueError("key-word not provided")
                else:
                    nkwds[key].append(s)
        nkwds = {k: ast.literal_eval(" ".join(nkwds[k]))
                 for k in nkwds}

        # get function kwds and form dict for templating
        func_kwds = genkwds(func, *args, **kwds)
        form = {**nkwds, **dict(func_kwds)}

        # update kwds to reflect new kwds
        for k in func_kwds:
            if k in nkwds:
                func_kwds[k] = nkwds[k]

        # update kwds to reflect template
        func_kwds = {k: Template(func_kwds[k]).render(**form)
                     if isinstance(func_kwds[k], str)
                     else func_kwds[k]
                     for k in func_kwds}

        return func(**func_kwds)

    return nfunc
