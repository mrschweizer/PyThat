import xarray


def norm_on_FO(x, dim=None, f_max=2):
    """
    Normalize a given dataset x on the average of the FO signal around zero frequency.
    :param x: xarray object
    :param name: Name of the Frequency coordinate axis along which the frequency is to be selected
    :param f_max: specifies the width of the frequency area over which is to be normalized
    :return: normalized xarray object
    """
    return x/x.where(abs(x[dim]) < f_max).mean(dim).squeeze()


def mask_FO(x, dim=None, f_max=2):
    """
    Mask an array around the center frequency.
    :param x: xarray object
    :param name: Name of the Frequency coordinate axis along which the frequency is to be Masked.
    :param f_max: specifies the width of the frequency area over which is to be normalized
    :return: xarray object where the frequencies around f=0 are set to nan
    """
    return x.where(abs(x[dim]) >= f_max)


def subtract_background(x, y, dim=None, f_max=2, f_min = None):
    """
    Use a reference measurement to substract the background. Background is renormalized to match the intensity of the
    main measurement in the specified interval and then substracted from the main. Can be used to substract things such
    as laser modes.
    :param x: xarray object
    :param y: xarray object (background)
    :param name: Name of the Frequency coordinate axis along which the frequency is to be selected
    :param f_max: specifies the maximum of the frequency area over which is to be normalized
    :param f_min: specifies the minimum of the frequency area over which is to be normalized. Defaults to -
    :return: x without background, xarray object
    """
    if f_min is None:
        f_min = -abs(f_max)
    norm = x.sel({dim: slice(f_min, f_max)}).sum(dim)
    return x - y/y.sel({dim: slice(f_min, f_max)}).sum(dim)*norm

def mask_all_zeros(x, dims, value=0):
    """
    Function that returns NAN, when all values in the space spun by dims have the same value as value.
    :param x: Xarray.DataArray or xarray.Dataset
    :param dims: Iterable of Hashable
    :param value: The value which is to be filtered.
    :return: The input data where spaces in which all values equal value are replaces by NAN.
    """
    mask = (x == value)
    for dim in dims:
        mask = mask.all(dim)
    return x.where(~mask)


def center_of_mass(da, dim, f_min=None, f_max=None):
    """
    Find the average value of a coordinate with values of statistical data (e.g. a peak in a spectrum)
    :param da: xarray.DataArray for evaluation
    :param dim: dimension along which the tracking should happen
    :param f_min: minimum value of detection range
    :param f_max: maximum value of detection range
    :return: xarray.DataArray with coordinate value of the center of mass
    """
    weight = da.sel(Frequency_1=slice(f_min, f_max))
    f = da[dim].weighted(weight).mean(dim)
    return f


def find_edge(da, dim, f_min=None, f_max=None, flank = 'positive', log_detect = False, norm=False):
    """
    This function uses a simple center of mass approach to treck edges in the signal.\n
    It can improve the signal, when the slope of the edge spans across multiple data points.
    :param da: xarray.DataArray for evaluation
    :param dim: dimension along which the edge tracking should happen
    :param f_min: minimum value for detection of the edge
    :param f_max: maximum value for detection of the edge
    :param flank: can be 'positive' or 'negative', depending on the direction of the edge
    :param log_detect: use logarithmic detection, can be helpful for exponential edges
    :param norm: normalize data before edge detection
    :return: xarray.DataArray with coordinate value of the center of mass of the selected edge
    """
    from numpy import log
    if log_detect:
        da = da.rolling(dict(Frequency_1=5)).mean()
        da = log(da.where(da>0))
    da_diff = da.differentiate(dim)
    da_diff = da_diff.sel(Frequency_1=slice(f_min, f_max))
    if flank == 'negative':
        da_diff = -da_diff
    elif flank == 'positive':
        pass
    if norm:
        da_diff = da_diff/da_diff.max(dim)
    if not log_detect:
        da_diff = da_diff.where((da_diff >= 0), 0)
    da_diff = da_diff.fillna(0)
    da_diff = da_diff.where(da_diff>0, 0).fillna(0)
    f = da[dim].weighted(da_diff).mean(dim)
    return f


xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
xarray.DataArray.mask_FO = mask_FO
xarray.Dataset.mask_FO = mask_FO
xarray.DataArray.subtract_background = subtract_background
xarray.Dataset.subtract_background = subtract_background
xarray.DataArray.mask_all_zeros = mask_all_zeros
xarray.Dataset.mask_all_zeros = mask_all_zeros