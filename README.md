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

```
from PyThat import MeasurementTree
import xarray as xr
import matplotlib.pyplot as plt

# define path to h5 file, can be relative or absolute path
path = r'M486 Dispersion 40 mT.h5'

index = None
# Optional: If the index is known beforehand, it can be specified here.
# Otherwise the user will be asked to choose by a popup.
# index = (2,1)

measurement_tree = MeasurementTree(path, index=index)
data: xr.DataArray = measurement_tree.array

# data can now be used as a usual xarray object
data.plot()
plt.show()
```