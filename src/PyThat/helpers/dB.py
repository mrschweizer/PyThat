import numpy as np
import xarray

def dB_to_lin(x):
    return np.power(10, x/10)

xarray.DataArray.dB_to_lin = dB_to_lin
xarray.Dataset.dB_to_lin = dB_to_lin

def lin_to_dB(x, ref=1):
    return 10*np.log10(x/ref)

xarray.DataArray.lin_to_dB = lin_to_dB
xarray.Dataset.lin_to_dB = lin_to_dB
