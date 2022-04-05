from PyThat import MeasurementTree
# from h5to_nc import MeasurementTree
import xarray as xr
import matplotlib.pyplot as plt

# Define path to .h5 file
path = r'D:\Pycharm\PyThat\examples\floquet_just_spectrum_analyzer_large_incomplete.h5'

index = (3, 0)
# Optional: If the index is known beforehand, it can be specified here. Otherwise the user will be asked to choose.
# index = (2, 1)

# Create measurement_tree object. Path argument should point towards thatec h5 file.
measurement_tree = MeasurementTree(path, index=index, override=True)

print(measurement_tree.logs)
print(measurement_tree.definition)
print(measurement_tree.labbook)
print(measurement_tree.tree_string)

data: xr.DataArray = measurement_tree.array
data.isel({'Set Magnetic Field': 5}).plot()


plt.show()
