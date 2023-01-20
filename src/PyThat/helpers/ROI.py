import xarray as xr


def monotone_divide(x: xr.DataArray or xr.Dataset, dim=None):
    if dim is None:
        raise ValueError('dim needs to be specified.')
    dx = x.diff(dim)
    print(x)
    incr = dx > 0
    decr = dx < 0
    _connected_(incr)
    print(incr, incr.shape)
    print(decr, decr.shape)

def _connected_(x):
    for i, y in enumerate(x):
        print('____')
        print(i, y)
        y0 = i
        if y:





if __name__ == '__main__':
    x = xr.DataArray([1, 2, 4, 4, 3], dims=('y'))
    monotone_divide(x, 'y')
