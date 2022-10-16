![logo](https://raw.githubusercontent.com/mrschweizer/PyThat/b57272fdf031b14097bd2b5f8d8cc44dfc1adf57/logo/PyThat_Logo.svg)
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

If you are using Conda/Anaconda, you can also install via pip. However, this may result in some dependency issues, rendering PyThat inoperable.

# Usage
The package reconstructs the measurement tree and lets the user choose the row containing an indicator.
It then uses the metadata from the measurement tree to construct an xarray object with n+m dimensions, where n is
the dimension of the indicator in the specified row and m the number of indents/loops.

Since xarray is built around labeled arrays, it also reconstructs the coord and dims attributes of the xarray objects.
For use of xarray see the [documentation](http://xarray.pydata.org/en/stable/user-guide/index.html#).

After starting at version 0.27 all data is read for all valid indicators and combined to a dataset.
The old version with indexing should still work, however.

For usage example, see [PyThat Documentation](https://pythat.readthedocs.io/en/latest/).