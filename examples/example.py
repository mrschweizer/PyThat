from PyThat import MeasurementTree
import xarray as xr
import matplotlib.pyplot as plt

# Define path to .h5 file
path = r'M486 Dispersion 40 mT.h5'

index = None
# Optional: If the index is known beforehand, it can be specified here. Otherwise the user will be asked to choose.
# index = (2, 1)

# Create measurement_tree object. Path argument should point towards thatec h5 file.
measurement_tree = MeasurementTree(path, index=index)

data: xr.DataArray = measurement_tree.array
data.sel({'Set Field': 40}, method='nearest').sel({'Frequency': slice(-15, -5, None)}).plot()
plt.show()
