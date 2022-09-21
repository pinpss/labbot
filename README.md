# labbot
A robot research assistant for Python.

labbot consists of a collection of decorators which support common patterns in research code.

## Usage

Labbot introduces a series of decorators which can be applied to any Python function to handle common additional functionality.  The following example shows the standard pattern for using labbot:

```python
import labbot as lb


def tfunc(a, b, c=1):

    print(c)
    return a + b + c


dec = lb.compose(lb.cachedec,
                 lb.dpart(iterdec, "c"))
dec(tfunc)(10, 20, c=[1, 2, 3, 4])
```

`cachedec` and `iterdec` are both decorators from labbot.  `compose` takes a list of decorators and combines them into one.  `dpart` creates a partial version of the decorator using additional inputs.

### cachedec

`cachedec` allows the user to record whether a particular set of params and code have been called with this function before.  It uses the joblib memory module to log each instance of the function run and can skip repeated instances where the code and params match.

### datalocdec

`datalocdec` can create the provided directory path if it doesn't exist and records a log of the directory path similar to `cachedec`.

```python
import labbot as lb
import pandas as pd
import numpy as np
import os


def tfunc(N, p, out_dir):

    df = pd.DataFrame(np.random.normal(size=(N, p)))
    df.to_csv(os.path.join(out_dir, "test.csv"),
              index=False)

dec = lb.compose(lb.cachedec,
                 lb.dpart(lb.datalocdec, "out_dir"))

out_dir = "/home/labbot/test"

dec(tfunc)(100, 10, out_dir)
```

### iterdec

`iterdec` is one of the most useful decorators provided by labbot.  It can allow the user to rerun a function with different parameter inputs automatically.  In the example above, `tfunc` will be run four times, once with each of the provided values for `c`.

#### jinja2

`iterdec` also has some useful functionality for templating inputs and file paths.  Inputs can be jinja2 templates and `iterdec` will use other available inputs to fill in the templates:

```python
import labbot as lb
import pandas as pd
import numpy as np
import os


def tfunc(N, p, out_dir):

    df = pd.DataFrame(np.random.normal(size=(N, p)))
    df.to_csv(os.path.join(out_dir, "test.csv"),
              index=False)

out_dir = "/home/labbot/{{dname}}_{{p}}"
dname_l = ["foo", "bar", "baz"]
p_l = [5, 10, 20]

dec = lb.compose(lb.cachedec,
                 lb.dpart(lb.datalocdec, "out_dir"),
                 lb.dpart(lb.iterdec, "p",
                          temp_keys=["out_dir"],
                          iter_kwds={"dname": dname_l}))

dec(tfunc)(100, p=p_l, out_dir=out_dir)
```

This will create a separate directory for each `dname`/`p` pair and write the corresponding csv to each directory.

#### zip

By providing an additional list of `zip_keys` we can change the desired behavior of `iterdec` to treat a specified subset of the iterable inputs as pairs in the same iteration:

```python
dec = lb.compose(lb.cachedec,
                 lb.dpart(lb.datalocdec, "out_dir"),
                 lb.dpart(lb.iterdec, "p",
                          temp_keys=["out_dir"],
                          zip_keys=["p", "dname"],
                          iter_kwds={"dname": dname_l}))
```

This will instead zip the arguments, key-words, or iterator key-words provided in `zip_keys` and treat them as tuples of inputs instead.

The result will be that this version of the code will only create directories, `foo_5`, `bar_10`, and `baz_20`.

#### joblib

Finally, `iterdec` also allows easy support for parallel runs of jobs.  Just drop the number of `n_jobs` in for the number of parallel workers and joblib will handle the rest:

```python
dec = lb.compose(lb.cachedec,
                 lb.dpart(lb.datalocdec, "out_dir"),
                 lb.dpart(lb.iterdec, "p", n_jobs=2,
                          temp_keys=["out_dir"],
                          zip_keys=["p", "dname"],
                          iter_kwds={"dname": dname_l}))
```

### errordec

`errordec` can rerun failed code however many times a user desires:

```python
dec = lb.compose(lb.cachedec,
                 lb.dpart(lb.datalocdec, "out_dir"),
                 lb.dpart(lb.errordec, retries=2, retry_delay=10,
                 lb.dpart(lb.iterdec, "p",
                          temp_keys=["out_dir"],
                          zip_keys=["p", "dname"],
                          iter_kwds={"dname": dname_l}))
```

In this example, the decorator will retry the underlying function twice with a delay of 10 seconds between each attempt.  This can be extremely useful when writing code which interacts with online or unstable resources.

### profiledec

`profiledec` is an easy tool for tracking how long different parts of a function run.  It uses the line_profiler package to record the runtime of each line of a given function and writes the result to a timestamped file in the source directory.

```python
dec = lb.compose(lb.profiledec,
                 lb.dpart(lb.datalocdec, "out_dir"),
                 lb.dpart(lb.errordec, retries=2, retry_delay=10,
                 lb.dpart(lb.iterdec, "p",
                          temp_keys=["out_dir"],
                          zip_keys=["p", "dname"],
                          iter_kwds={"dname": dname_l}))
```

### clidec

`clidec` is a useful way to parameterize functions with command line arguments.  When it is added to the overall decorator it allows the users to pass in flags for various args and kwargs from the command line, for instance, if you add to your runscript:

```python
dec = lb.compose(lb.clidec)
dec(foo)(iterations, chars)
```

```bash
run runscript.py --iterations 100
```

Would run the `foo` with iterations set to 100.  Any txt after a flag is converted into a single string and then passed to literal eval, allowing inputs to be basic python types.  For instance,

```bash
run runscript.py --chars ["size", "value"]
```

Would pass in the variable `chars` into `foo` with a list of `"size"` and `"value"`.

Note that `clidec` can also handle inputs that correspond to format inputs comparable to `iter_kwds` in `iterdec`.
