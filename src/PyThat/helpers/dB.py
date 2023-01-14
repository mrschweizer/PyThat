import numpy as np

def dB_to_lin(x):
    return np.power(10, x/10)

def lin_to_dB(x, ref=1):
    return 10*np.log10(x/ref)