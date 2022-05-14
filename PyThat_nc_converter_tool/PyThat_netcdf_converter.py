from sys import argv
from PyThat import MeasurementTree
import pathlib

try:
    path = pathlib.Path(argv[1]).absolute()
except IndexError:
    print(r'Please specifiy a full path, e.g. D:\files\my_data.h5')
    path = pathlib.Path(input()).absolute()
MeasurementTree(path, override=True, index=True)
