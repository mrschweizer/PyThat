import xarray

def foo(x):
    print(x)

xarray.DataArray.foo = foo
xarray.Dataset.foo = foo

def norm_on_FO(x, name='Frequency' ,f_max=2):
    return x/x.where(abs(x[name]) < f_max).mean(name).squeeze()

xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
