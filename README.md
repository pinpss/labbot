# labbot
A robot research assistant for Python.

labbot consists of a collection of decorators which support common patterns in research code.

## Usage

```python
import labbot as lb


def tfunc(a, b, c=1):

    print(c)
    return a + b + c


dec = lb.compose(lb.cachedec,
                 lb.dpart(iterdec, "c"))
dec(tfunc)(10, 20, c=[1, 2, 3, 4])
```

### cachedec

```python
```

### datalocdec

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

#### jinja2

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
                          zip_kwds=["p", "dname"],
                          iter_kwds={"dname": dname_l}))

dec(tfunc)(100, p=p_l, out_dir=out_dir)
```

This will instead zip the arguments, key-words, or iterator key-words provided in `zip_kwds` and treat them as tuples of inputs instead.

The result will be that this version of the code will only create directories, `foo_5`, `bar_10`, and `baz_20`.

### errordec

```python
```

### profiledec

```python
import labbot as lb
import pandas as pd
import numpy as np
import os


def tfunc(N, p, out_dir):

    df = pd.DataFrame(np.random.normal(size=(N, p)))
    df.to_csv(os.path.join(out_dir, "test.csv"),
              index=False)

dec = lb.compose(lb.profiledec,
                 lb.dpart(lb.datalocdec, "out_dir"))

out_dir = "/home/labbot/test"

dec(tfunc)(100, 10, out_dir)
```
