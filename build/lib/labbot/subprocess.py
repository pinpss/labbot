"""
decorator to run function as subprocess
"""
from boltons.funcutils import wraps
from .utilities import genkwds
import subprocess
import inspect
import shutil
import joblib
import json
import os

# TODO this is currently not in use, should remove


def subprocessdec(func, jobtype="source", cache_dir="."):
    """calls function as subprocess (allows for nested multiprocessing)"""

    @wraps(func)
    def nfunc(*args, **kwds):

        # collapse args into kwds to dump to json
        nkwds = genkwds(func, *args, **kwds)
        kwds_hash = joblib.hash(nkwds)

        # handle different jobtypes
        if jobtype == "source":
            mod_lab = "mod_%s" % kwds_hash
        elif jobtype == "module":
            mod_lab = func.__module__
        else:
            raise ValueError("Unknown jobtype: %s" % jobtype)

        # prep file names
        loc = os.path.join(cache_dir, ".labbot", "subprocessdec_tmp_files")
        os.makedirs(loc, exist_ok=True)
        run_f = "run_%s.py" % kwds_hash
        mod_f = "%s.py" % mod_lab
        json_f = "%s.json" % kwds_hash

        # create module file containing code from func
        mod_script = inspect.getfile(func)
        shutil.copy(mod_script, os.path.join(loc, mod_f))

        # prep run script
        fn_name = func.__name__
        with open(os.path.join(loc, run_f), "w") as fd:
            fd.write("from %s import %s as func\n" % (mod_lab, fn_name))
            fd.write("import json\n")
            fd.write("\n")
            fd.write("json_file = '%s'\n" % json_f)
            fd.write("\n")
            fd.write("with open(json_file, 'r') as fd:\n")
            fd.write("    func_kwds = json.load(fd)\n")
            fd.write("\n")
            fd.write("func(**func_kwds)\n")

        # prep kwds/json
        with open(os.path.join(loc, json_f), "w") as fd:
            json.dump(nkwds, fd)

        # run code
        process = subprocess.Popen(["python", run_f], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=loc)

        # while there is output coming from the process write
        # it to the logger
        with process.stdout as pipe:
            for line in iter(pipe.readline, b""):
                print("subprocess output: %s" % line)

        # catch the return code, if it is non-zero something has
        # gone wrong and we need to throw a CalledProcessError
        retcode = process.wait()

        if retcode:
            raise subprocess.CalledProcessError(retcode, "python %s" % run_f)

        # remove script files
        os.remove(os.path.join(loc, mod_f))
        os.remove(os.path.join(loc, json_f))
        os.remove(os.path.join(loc, run_f))

    return nfunc
