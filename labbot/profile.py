from contextlib import redirect_stdout
from line_profiler import LineProfiler
from boltons.funcutils import wraps
from datetime import datetime


def profiledec(func):

    profiler = LineProfiler()
    profiled_func = profiler(func)

    @wraps(func)
    def nfunc(*args, **kwds):

        try:
            return profiled_func(*args, **kwds)
        finally:
            t0 = datetime.now()
            fpath = t0.strftime("%Y%m%d%H%M%S.txt")
            with open(fpath, "w") as f:
                with redirect_stdout(f):
                    profiler.print_stats()

    return nfunc
