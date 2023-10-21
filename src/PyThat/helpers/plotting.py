from matplotlib.colors import LinearSegmentedColormap
from cycler import cycler
from numpy import linspace

cold_to_hot = LinearSegmentedColormap.from_list('cold_to_hod', ['mediumblue', 'darkorchid', 'red'])

def cmap_to_cycler(cmap, n):
    colors = cmap(linspace(0, 1, n))
    return cycler(color=colors)
