import xarray as xr
import numpy as np


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


from typing import Iterable, Dict


def slice_accumulate(x: xr.Dataset or xr.DataArray, edges: Dict[str, Iterable[float]], method='sum'):
    for key, value in edges.items():
        coord_range_edges = list(zip(value, value[1::]))
        coord_ranges = [slice(*edge_pair, None) for edge_pair in coord_range_edges]
        slices_one_dimension = [x.sel({key: coord_range}) for coord_range in coord_ranges]
        if method == 'mean':
            slices_one_dimension = [el.mean(key) for el in slices_one_dimension]
        elif method == 'sum':
            slices_one_dimension = [el.sum(key) for el in slices_one_dimension]
        x = xr.concat(slices_one_dimension, key)
        x = x.assign_coords({key: [str(x) for x in coord_range_edges]})
    return x


xr.DataArray.slice_accumulate = slice_accumulate
xr.Dataset.slice_accumulate = slice_accumulate


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    a = np.linspace(-5, 5, 11)
    b = np.linspace(-7, 7, 15)
    A, B = np.meshgrid(a, b, indexing='ij')
    C = A**2+B**2
    array = xr.DataArray(C, dims=('x', 'y'), coords={'x': a, 'y': b})
    slice_accumulate(array, {'x': [-5, -2, 3, 5], 'y': [-7, -4, 2, 5]}, method='mean').plot(x='x', y='y')
    plt.show()
