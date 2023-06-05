"""
decorates function to handle failures/rerun
"""
from boltons.funcutils import wraps
import time


def errordec(func, retries=0, retry_delay=5, raise_error=True):
    """handles retries and error states

    Parameters
    ----------
    func : function
        function to be decorated
    retries : scalar
        number of times to try rerunning the code on failure
    retry_delay : scalar
        number of seconds to wait between each rety
    raise_error : bool
        whether to pass up errors or catch and convert to a warning

    Returns
    -------
    function
        decorated to handle errors
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        # handle retries
        for r in range(retries):
            try:
                return func(*args, **kwds)
            except Exception as e:
                print(e)
                pass

            time.sleep(retry_delay)

        # note we don't need an else statement here because by iterating
        # over the retries we should still have one real try left
        try:
            return func(*args, **kwds)
        except Exception as e:
            if raise_error:
                raise e

    return nfunc
