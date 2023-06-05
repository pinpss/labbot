"""
formats templatable inputs
"""
from .utilities import genkwds
from functools import wraps
from jinja2 import Template


def templatedec(func, *tempkeys, label=None):
    """assumes the tempkeys are jinja2 templates and populates with inputs

    Parameters
    ----------
    func : function
        function to decorate
    tempkeys : iterable
        iterable of keys to template
    label : str or None
        if provided, this is a template which we populate before passing
        into the other templates

    Returns
    -------
    func : function
        decorated to handle templating
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        func_kwds = genkwds(func, *args, **kwds)
        form = dict(func_kwds)

        # render label if provided
        if label:
            nlabel = Template(label).render(**form)
            form["label"] = nlabel

        # update kwds to reflect template
        func_kwds = {k: Template(func_kwds[k]).render(**form)
                     if isinstance(func_kwds[k], str)
                     else func_kwds[k]
                     for k in func_kwds}

        return func(**func_kwds)

    return nfunc
