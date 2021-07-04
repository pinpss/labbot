"""
combines an iterable dec and template dec for cases where we have patterns in
input and output paths which we'd like to iterate over (fairly common)
"""
from jinja2 import Template, DebugUndefined
from joblib import Parallel, delayed
from boltons.funcutils import wraps
from .utilities import genkwds
import itertools
import time


def iterdec(func, *iter_keys, temp_keys=[], zip_keys=[], iter_kwds={},
            n_jobs=1, wait=0):
    """converts a single run of a function into many

    Parameters
    ----------
    func : function
        function to decorate
    iter_keys : iterable
        list of func inputs which we iterate over
    temp_keys : iterable
        iterable of func kwds which we need to template
    zip_keys : iterable
        iterable of func kwds which are treated as the same iteration
    iter_kwds : dict
        dictionary mapping template inputs to list of values
    n_jobs : scalar
        number of jobs for possible parallel estimation
    wait : scalar
        wait between each job launch

    Returns
    -------
    func : function
        decorated to handle iteration

    Notes
    -----
    Can run functions with several options:

    1. sequentially

    2. in parallel with joblib
    """


    @wraps(func)
    def nfunc(*args, **kwds):

        func_kwds = genkwds(func, *args, **kwds)
        n_iter_kwds = {**{k: func_kwds[k] for k in iter_keys}, **iter_kwds}
        gen_tasks = iter_task(func_kwds, iter_keys, temp_keys, zip_keys,
                              n_iter_kwds)

        # offset function for wait
        ofn = lambda i: i - n_jobs * int((i * 1.) / n_jobs)

        if n_jobs != 1 and wait == 0:
            res = Parallel(n_jobs=n_jobs)(delayed(func)(**t_kwds)
                                          for t_kwds in gen_tasks)
        elif n_jobs != 1 and wait > 0:
            res = Parallel(n_jobs=n_jobs)(
                delayed(_waitfn)(ofn(i), func, wait, **t_kwds)
                for i, t_kwds in enumerate(gen_tasks))
        elif n_jobs == 1 and wait == 0:
            res = [func(**t_kwds) for t_kwds in gen_tasks]
        elif n_jobs == 1 and wait > 0:
            res = [_waitfn(1, func, wait, **t_kwds) for t_kwds in gen_tasks]

        return res

    return nfunc


def _waitfn(ind, func, wait, *args, **kwds):
    """waits based on ind and then runs func"""

    time.sleep(wait * ind)
    return func(*args, **kwds)


def iter_task(func_kwds, iter_keys, temp_keys, zip_keys, iter_kwds):
    """convert kwds into list of kwds based on iter_keys

    Parameters
    ----------
    func_kwds : dict
        dictionary of inputs passed to func
    iter_keys : iterable
        list of func inputs which we iterate over
    temp_keys : iterable
        iterable of func kwds which we need to template
    zip_keys : iterable
        iterable of func kwds which are treated as the same iteration
    iter_kwds : dict
        dictionary mapping template inputs to list of values

    Yields
    ------
    dict
        key words for current iterable element
    """

    # split zip keys to zip
    f_iter_kwds = {}
    z_iter_kwds = {}
    for k in iter_kwds:
        if k in zip_keys:
            z_iter_kwds[k] = iter_kwds[k]
        else:
            f_iter_kwds[k] = iter_kwds[k]

    z_iter_k = list(z_iter_kwds.keys())
    z_iter_v = list(z_iter_kwds.values())
    z_iter_v = list(zip(*z_iter_v))
    f_iter_k = list(f_iter_kwds.keys())
    f_iter_v = list(f_iter_kwds.values())
    iter_k = z_iter_k + f_iter_k

    # build all possible products of baseline kwds
    f_iter_prods = list(itertools.product(*f_iter_v))

    # handle additional cases for zipped kwds
    iter_prods = []
    for zv in z_iter_v:
        for p in f_iter_prods:
            np = list(zv) + list(p)
            iter_prods.append(np)

    for prod in iter_prods:

        temp_kwds = {k: v for k, v in zip(iter_k, prod)}

        n_func_kwds = {}
        for k in func_kwds:
            if k in iter_keys:
                n_func_kwds[k] = temp_kwds[k]
            elif k in temp_keys:
                tmp = Template(func_kwds[k], undefined=DebugUndefined)
                n_func_kwds[k] = tmp.render(**temp_kwds)
            else:
                n_func_kwds[k] = func_kwds[k]

        yield n_func_kwds
