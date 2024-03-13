from matplotlib.colors import LinearSegmentedColormap, to_hex
from cycler import cycler
from numpy import linspace, meshgrid
import matplotlib.pyplot as plt

cold_to_hot = LinearSegmentedColormap.from_list('cold_to_hod', ['mediumblue', 'darkorchid', 'red'])

default_styles = {
    'linestyle': ['solid', 'dashed', 'dotted', 'dashdot']
}

style_generators = {
    'alpha': lambda x: linspace(1, 0.3, x),
    'linewidth': lambda x: 0.5 + linspace(0, 1, x)*1.5
}


def get_styles(key, size):
    items = []
    for i in plt.rcParams['axes.prop_cycle']:
        items.append(i)
    list_dict = {}
    for i in items:
        for j, k in i.items():
            if j not in list_dict.keys():
                list_dict[j] = [k]
            else:
                list_dict[j].append(k)
    for i, j in default_styles.items():
        if i not in list_dict.keys():
            list_dict[i] = j
    if key in list_dict.keys():
        return list_dict[key][:size]
    elif key in style_generators.keys():
        return style_generators[key](size)
    else:
        raise ValueError('theres no default for this styling parameter')


def conv_colors(colors):
    new_colors = []
    for x in colors:
        new_colors.append(to_hex(x))
    return new_colors


def cmap_to_cycler(cmap, n, lin_range=(0, 1)):
    colors = cmap(linspace(*lin_range, n))
    return cycler(color=colors)


def multidim_cycler(**m):
    if 'color' in m.keys():
        updated_colors = []
        for z in m['color']:
            v = to_hex(z) if not isinstance(z, str) else z
            updated_colors.append(v)
        m['color'] = updated_colors
    v = meshgrid(*m.values(), indexing='ij')
    v = [cycler(**{k: x.ravel()}) for k, x in zip(m.keys(), v)]
    cyc = None
    for i, x in enumerate(v):
        if i == 0:
            cyc = cycler(x)
        else:
            cyc = cyc + x
    return cyc


def _check_styles(da, styles):
    style_values = []
    for i in styles.keys():
        q = styles[i]
        y = da.sizes[i]
        if isinstance(q, str):
            style_values.append((q, get_styles(q, y)))
        elif isinstance(q, tuple):
            if len(q[1]) != y:
                raise ValueError('dimenseions of styles and da do not match')
            else:
                style_values.append((q[0], q[1]))
    return style_values


def plot_multidim_line(da, styles=None, x=None, hue=None, ax=None, multidim_name='m'):
    """
    Wrapper for xarray.plot.line to plot the data, so that every dimension is associated to a line style parameter\
    (like hue)
    :param da: The DataArray used for the generation of the cycler
up    :param styles: dict of tuples: {dimension name: (style parameter, list of style values)}, or dict of str with matplotlib lineproperties names
    :param x: hashable, axis which is to be plotted on the x-axis
    :param hue: Coordinate which will be passed on to the plotting routine
    :param ax: axes to be plotted to
    :param multidim_name: name of the multi_dim variable, mostly for internal use
    :return:
    """

    if ax is None:
        fig, ax = plt.subplots()
    if multidim_name in da.dims:
        raise AttributeError('multidim name is already used')
    dims = list(styles.keys())
    style_values = _check_styles(da, styles)
    da_red = da.stack(**{multidim_name: dims}, create_index=False)
    c_cycler = multidim_cycler(**dict(style_values))
    ax.set_prop_cycle(c_cycler)
    da_red.plot(x=x, hue=hue, ax=ax)
