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


xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
xarray.DataArray.mask_FO = mask_FO
xarray.Dataset.mask_FO = mask_FO
xarray.DataArray.subtract_background = subtract_background
xarray.Dataset.subtract_background = subtract_background
xarray.DataArray.mask_all_zeros = mask_all_zeros
xarray.Dataset.mask_all_zeros = mask_all_zeros