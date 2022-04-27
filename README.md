# Project Description
This is a community package which helps reading .h5 files created by ThatecOS and converting them to xarray objects and
netcdf files. This software is not maintained by and has no affiliations to THATec Innovation GmbH.
# Installation
```$ pip install PyThat```

If not happened automatically, install following dependencies:
netcdf4,
scipy,
h5netcdf,
h5py,
xarray

# Usage
The package reconstructs the measurement tree and lets the user choose the row containing an indicator.
It then uses the metadata from the measurement tree to construct an xarray object with n+m dimensions, where n is
the dimension of the indicator in the specified row and m the number of indents/loops.

Since xarray is built around labeled arrays, it also reconstructs the coord and dims attributes of the xarray objects.
For use of xarray see the [documentation](http://xarray.pydata.org/en/stable/user-guide/index.html#).

After starting at version 0.27 all data is read for all valid indicators and combined to a dataset.
The old version with indexing should still work, however.

```
from PyThat import MeasurementTree
import xarray as xr
import matplotlib.pyplot as plt

# define path to h5 file, can be relative or absolute path
path = r'D:\Pycharm\PyThat\examples\M486 Dispersion 40 mT.h5'

# Get dataset from file
data = MeasurementTree(path, override=True).dataset
print(data)

# Get variable name from printout
interesting_name = "2,1: Acquire spectrum"
interesting_data = data[interesting] 

# Select and plot data
interesting_data.sel(dict(Frequency=slice(5, 15, None))).plot(col='Set Field')
plt.show()
```