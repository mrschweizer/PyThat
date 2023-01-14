import xarray

def foo(x):
    print(x)

xarray.DataArray.foo = foo
xarray.Dataset.foo = foo

def norm_on_FO(x, name='Frequency' ,f_max=2):
    """
    Normalize a given dataset x on the average of the FO signal around zero frequency.
    :param x: xarray object
    :param name: Name of the Frequency coordinate axis along which the frequency is to be selected
    :param f_max: specifies the width of the frequency area over which is to be normalized
    :return: normalized xarray object
    """
    return x/x.where(abs(x[name]) < f_max).mean(name).squeeze()

xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
