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


xarray.DataArray.norm_on_FO = norm_on_FO
xarray.Dataset.norm_on_FO = norm_on_FO
xarray.DataArray.mask_FO = mask_FO
xarray.Dataset.mask_FO = mask_FO
