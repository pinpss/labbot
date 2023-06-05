import inspect


def genkwds(func, *args, **kwds):
    """joins args into kwds"""

    func_spec = unwrap_fullargspec(func)
    defaults = func_spec.defaults
    func_args = func_spec.args
    kwds = {**{a: av for a, av in zip(func_args, args)}, **kwds}
    # NOTE this worked for old code but breaks now
    # must have been some change in the func_spec setup
#    if defaults:
#        func_args = func_args[:-len(defaults)]
#    kwds = {**{a: av for a, av in zip(func_args, args)}, **kwds}

    return kwds


def unwrap_fullargspec(func):
    """recursively searches through wrapped function to get the args"""

    func_dict = func.__dict__
    if "__wrapped__" in func_dict:
        return unwrap_fullargspec(func_dict["__wrapped__"])
    else:
        return inspect.getfullargspec(func)
