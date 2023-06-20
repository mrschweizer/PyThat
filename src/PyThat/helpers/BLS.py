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

def substract_background(x, y, dim=None, f_max=2, f_min = None):
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


xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
xarray.DataArray.mask_FO = mask_FO
xarray.Dataset.mask_FO = mask_FO
xarray.DataArray.substract_background = substract_background
xarray.Dataset.substract_background = substract_background
