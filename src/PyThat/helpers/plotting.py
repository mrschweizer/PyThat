from matplotlib.colors import LinearSegmentedColormap
from cycler import cycler
from numpy import linspace, meshgrid
import matplotlib.pyplot as plt

cold_to_hot = LinearSegmentedColormap.from_list('cold_to_hod', ['mediumblue', 'darkorchid', 'red'])

def cmap_to_cycler(cmap, n):
    colors = cmap(linspace(0, 1, n))
    return cycler(color=colors)

def multidim_cycler(**m):
    v = meshgrid(*m.values(), indexing='ij')
    v = [cycler(**{k: x.ravel()}) for k, x in zip(m.keys(), v)]
    for i, x in enumerate(v):
        if i == 0:
            cyc = cycler(x)
        else:
            cyc = cyc + x
    return cyc

def plot_multidim_line(da, styles=None, x=None, hue=None, ax=None, multidim_name='m'):
    """
    Wrapper for xarray.plot.line to plot the data, so that every dimension is associated to a line style parameter (like hue)
    :param da: The DataArray used for the generation of the cycler
    :param styles: dict of tuples: {dimension name: (style parameter, list of style values)}
    :param label: name of the dimension used for labels
    :param ax: axes to be plotted to
    :param multidim_name: name of the multi_dim variable, mostly for internal use
    :return:
    """

    if ax is None:
        fig, ax = plt.subplots()
    if multidim_name in da.dims:
        raise AttributeError('multidim name is already used')
    dims = list(styles.keys())
    data_sizes = {x: da.sizes[x] for x in dims}
    style_sizes = {x: len(y[1]) for x, y in styles.items()}
    if data_sizes != style_sizes:
        raise ValueError(f'styles does not have the same size as da {style_sizes}, {data_sizes}')
    da_red = da.stack(**{multidim_name: dims}, create_index=False)
    c_cycler = multidim_cycler(**dict(styles.values()))
    ax.set_prop_cycle(c_cycler)
    da_red.plot(x=x, hue=hue, ax=ax)