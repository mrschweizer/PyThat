import xarray as xr
from numpy import arange


# def monotone_divide(x: xr.DataArray or xr.Dataset, dim=None):
#     if dim is None:
#         raise ValueError('dim needs to be specified.')
#     dx = x.diff(dim)
#     print(x)
#     incr = dx > 0
#     right_end = (incr != incr.shift({dim: -1})).pad({dim: (1, 0)}, constant_values=False)
#     # left_end = (incr != incr.shift({dim: 1})).pad({dim: (1, 0)}, constant_values=False)
#     # print(x.where(arange(x.sizes[dim]), drop=True))
#     print(x[dim].where(right_end, drop=True))

# if __name__ == '__main__':
#     x = xr.DataArray(list(range(6))+[5, 5, 5]+list(range(4, 0, -1))+list(range(3, 9)), dims=('y'))
#     monotone_divide(x, 'y')
