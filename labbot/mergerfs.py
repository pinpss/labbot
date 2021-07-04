"""
decorator function to convert mergerfs path to base (for speed)
"""
from .utilities import unwrap_fullargspec
from boltons.funcutils import wraps
import xattr
import os


def mfsdec(func, *mf_dirs):
    """"updates paths to remove mergerfs layer

    Parameters
    ----------
    func : function
        function for which we'd to create output directories
    mf_dirs : tuple
        key labels for inputs which correspond to paths on a mergerfs
        mount which we'd like to replace with original drives

    Returns
    -------
    func : function
        decorated to add output directories
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        # update args
        # TODO most of this code is from genkwds
        func_spec = unwrap_fullargspec(func)
        defaults = func_spec.defaults
        func_args = func_spec.args
        if defaults:
            func_args = func_args[:-len(defaults)]

        nargs_l = []
        for ak, av in zip(func_args, args):
            if ak in mf_dirs:
                print(ak, av, "pre")
                loc = xattr.getxattr(av, "user.mergerfs.basepath")
                loc = loc.decode("utf-8")
                av = os.path.join(loc, os.path.basename(av))
                print(ak, av, "post")
                nargs_l.append(av)
            else:
                nargs_l.append(av)
        args = tuple(nargs_l)

        # update kwds
        nkwds = {}
        for k in kwds:
            v = kwds[k]
            if k in mf_dirs:
                loc = xattr.getxattr(v, "user.mergerfs.basepath")
                loc = os.path.basename(loc.decode("utf-8"))
                v = os.path.join(loc, os.path.basename(v))
                nkwds[k] = v
            else:
                nkwds[k] = v
        kwds = nkwds

        return func(*args, **kwds)


    return nfunc
