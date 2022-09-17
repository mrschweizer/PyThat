Usage
=====

Installation
------------

To use PyThat, first install it using pip (via terminal):

.. code-block:: console

   $ pip install PyThat

Please note, that PyThat is not yet available via conda/Anaconda.

Basics and Scope
----------------
The package reconstructs the measurement tree and lets the user choose the row containing an indicator. It then uses
the metadata from the measurement tree to construct an xarray object with n+m dimensions, where n is the dimension of
the indicator in the specified row and m the number of indents/loops.

Since xarray is built around labeled arrays, it also reconstructs the dimension label (dims) and label coordinate
(coords) attributes of the xarray objects. The scope of PyThat is the conversion into the xarray format. For use of
xarray see the well maintained `xarray documentation <https://docs.xarray.dev/en/stable/user-guide/index.html>`_.

After starting at version 0.27 all data is read for all valid indicators and combined to a dataset. The old version with indexing should still work, however.



Tutorial
========

Load Data
---------
.. code-block:: python

   from PyThat import MeasurementTree
   path = r'C:\some_folder\measurement_file.h5'
   mt = MeasurementTree(path)

This will create a ``MeasurementTree`` object ``mt`` in which the measurement data is stored.

The printout will look somewhat like this:

.. code-block:: console

   Number of groups: 2
   (0, 0) "row_00": ['scalar control', 'Anritsu ShockLine MS46xxx VNA', 'Number of points', 1001.0, 2147483647.0, 1.0]
   (0, 1) "row_01": ['scalar control', 'Anritsu ShockLine MS46xxx VNA', 'Start frequency (MHz)', 5650.0, 43499.999998, 1.0]
   (0, 2) "row_02": ['scalar control', 'Anritsu ShockLine MS46xxx VNA', 'Stop frequency (MHz)', 6350.0, 6350.0, 1.0]
   (0, 3) "row_03": ['scalar control', 'Anritsu ShockLine MS46xxx VNA', 'Averages', 10.0, 4294967295.0, 1.0]
   (0, 4) "row_04": ['boolean control', 'Bruker_B-EC1_Simple', 'DC Output', 'TRUE']
   (0, 5) "row_05": ['scalar control', 'Bruker_B-EC1_Simple', 'Set Magnetic Field (mT)', 130.0, 155.0, 21.0]
   (1, 0) "row_06": ['boolean control', 'Anritsu ShockLine MS46xxx VNA', 'Trigger spectrum', 'TRUE']
     (1, 1) "row_07": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Im_S11'] (21, 1001)
     (1, 2) "row_08": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Im_S12'] (21, 1001)
     (1, 3) "row_09": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Im_S21'] (21, 1001)
     (1, 4) "row_10": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Im_S22'] (21, 1001)
     (1, 5) "row_11": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Re_S11'] (21, 1001)
     (1, 6) "row_12": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Re_S12'] (21, 1001)
     (1, 7) "row_13": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Re_S21'] (21, 1001)
     (1, 8) "row_14": ['indicator', 'Anritsu ShockLine MS46xxx VNA', 'Re_S22'] (21, 1001)
   Core data names: ['Frequency', 'Amplitude', 'Frequency_1', 'Amplitude_1', 'Frequency_2', 'Amplitude_2', 'Frequency_3', 'Amplitude_3', 'Frequency_4', 'Amplitude_4', 'Frequency_5', 'Amplitude_5', 'Frequency_6', 'Amplitude_6', 'Frequency_7', 'Amplitude_7']

This is the representation of the scan definition. It shows all rows, their functions and dimensions.
"Core data names" is a list of variables inside the created xarray.Dataset.

Followed by a few blocks like this:

.. code-block:: console

   Building xarray object for:
   Im_S11, row_07
   ________________________________________________________
   Scalar control Set Magnetic Field without data. Generating coords.
   Get Metadata for: row_07

For each indicator row, a block like this will be printed. In the case of most sweeped controls,
no coordinate array is available. This means, this array must first be created, which is denoted here.

And finally:

.. code-block:: console

   Saved as C:\Users\Matthias\Desktop\PyThat Example\VNA_2_to_1True.nc

The process has finished and the file has been saved to a .nc file. If you run the same script again, this file will be
loaded instead of doing the whole process again.


Review Data Structure
---------------------

Once, the dataset has been created, you can access it via

>>> print(mt.dataset)
<xarray.Dataset>
Dimensions:             (Set Magnetic Field: 21, Frequency: 1001,
                         Frequency_1: 1001, Frequency_2: 1001,
                         Frequency_3: 1001, Frequency_4: 1001,
                         Frequency_5: 1001, Frequency_6: 1001, Frequency_7: 1001)
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_1         (Frequency_1) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_2         (Frequency_2) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_3         (Frequency_3) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_4         (Frequency_4) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_5         (Frequency_5) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_6         (Frequency_6) float64 5.65e+03 5.651e+03 ... 6.35e+03
  * Frequency_7         (Frequency_7) float64 5.65e+03 5.651e+03 ... 6.35e+03
Data variables:
    Im_S11              (Set Magnetic Field, Frequency) float64 0.4498 ... 0....
    Im_S12              (Set Magnetic Field, Frequency_1) float64 0.001696 .....
    Im_S21              (Set Magnetic Field, Frequency_2) float64 0.001506 .....
    Im_S22              (Set Magnetic Field, Frequency_3) float64 -0.1521 ......
    Re_S11              (Set Magnetic Field, Frequency_4) float64 -0.057 ... ...
    Re_S12              (Set Magnetic Field, Frequency_5) float64 0.002668 .....
    Re_S21              (Set Magnetic Field, Frequency_6) float64 0.002619 .....
    Re_S22              (Set Magnetic Field, Frequency_7) float64 -0.5101 ......

This output is rich in information. The first paragraph describes the found dimensions and corresponding shape. This
particular set of data has one dimension *Set Magnetic Field* and 8 *Frequency* dimensions, each with the same size.

The next paragraph denotes the corresponding coordinates. In this example, there are 9 coordinate arrays, each linked to
different dimension (denoted by the parentheses). On the right, an excerpt from the coordinate data is shown.

Indicator rows have been translated to data variables (e.g. Im_S11) and controls to coordinates (e.g. "Set Magnetic Field").
Since Im_S11 etc. are 1D data, they have also been assigned a frequency coordinate. The coordinate names have been chosen,
so that they are unique, in order to prevent different devices/functions having the same coordinate name.

In this example, all of the above Frequency dimensions, are equal and equivalent. They *are* the same quantity and not
just *coincidentally equal*. In this case, you should use ``PyThat.consolidate_dims`` to merge equivalent dimensions.

>>> from PyThat import consolidate_dims
>>> d = consolidate_dims(mt.dataset, 'Frequency')
>>> d
<xarray.Dataset>
Dimensions:             (Set Magnetic Field: 21, Frequency: 1001)
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
Data variables:
    Im_S11              (Set Magnetic Field, Frequency) float64 ...
    Im_S12              (Set Magnetic Field, Frequency) float64 ...
    Im_S21              (Set Magnetic Field, Frequency) float64 ...
    Im_S22              (Set Magnetic Field, Frequency) float64 ...
    Re_S11              (Set Magnetic Field, Frequency) float64 ...
    Re_S12              (Set Magnetic Field, Frequency) float64 ...
    Re_S21              (Set Magnetic Field, Frequency) float64 ...
    Re_S22              (Set Magnetic Field, Frequency) float64 ...

In the process, the dependencies of Data variables have also changed. Now, they are all linked to the same dimension
*Frequency*.

If you want more detailed information on the coordinates, you can call ``mt.dataset.coords``. ``mt.dataset.dims`` will
return a list of dimension names.

The data shows example data from a VNA. There are multiple S-parameters. Let's say you want to access a single parameter.
This can be done by using square brackets containing a string of the corresponding variable name (``'Im_S11'``), as shown in the printout:

>>> da = d['Im_S11']
>>> da
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 21, Frequency: 1001)>
array([[0.449762, 0.449024, 0.445432, ..., 0.315165, 0.280422, 0.244154],
       [0.446916, 0.448087, 0.446013, ..., 0.315432, 0.280684, 0.244377],
       [0.364744, 0.371938, 0.377282, ..., 0.315766, 0.280974, 0.244608],
       ...,
       [0.457564, 0.453792, 0.447533, ..., 0.332801, 0.298602, 0.262485],
       [0.457725, 0.454055, 0.447757, ..., 0.340996, 0.307394, 0.271574],
       [0.457942, 0.454288, 0.447996, ..., 0.364995, 0.332711, 0.298152]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
Attributes:
    units:

This returns an ``xarray.DataArray``. This is the starting point for all further evaluation.
The same approach can be used to retrieve the values of the *Frequency* coordinate axis: ``d['Frequency']`` from a
Dataset or ``da['Frequency']`` from a DataArray .

Disclaimer
""""""""""

Everything, that comes after this part, is **not** a proper tutorial, but rather a teaser of what you *can* do. Please
look at the `xarray documentation <https://docs.xarray.dev/en/stable/user-guide/index.html>`_ for further information.


Selecting Data
--------------

Let's say you are only interested in a certain Frequency range. From the previous section, we can already see, that the
Frequency coordinate contains an area from ``5.65e+03`` to ``6.35e+03`` MHz. There are two main methods for selecting data:

``da.sel`` is in most cases the most comfortable to use. It lets you select a *slice* of along a certain coordinate, by
specifiying start stop and interval. The actual indexing is done by xarray automatically. This can be done in a *kwarg*
notation:

>>> da.sel(Frequency=slice(5.6e3, 5.8e3, None))
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 21, Frequency: 215)>
array([[ 0.449762,  0.449024,  0.445432, ..., -0.424727, -0.446139, -0.466247],
       [ 0.446916,  0.448087,  0.446013, ..., -0.42421 , -0.445718, -0.465891],
       [ 0.364744,  0.371938,  0.377282, ..., -0.423051, -0.44466 , -0.464935],
       ...,
       [ 0.457564,  0.453792,  0.447533, ..., -0.440081, -0.460952, -0.480101],
       [ 0.457725,  0.454055,  0.447757, ..., -0.439938, -0.460871, -0.480055],
       [ 0.457942,  0.454288,  0.447996, ..., -0.439832, -0.460777, -0.479958]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 5.8e+03
Attributes:
    units:

Another way to supply the selection, is in form of a dictionary with curly brackets. The advantage of this notation is
the ability to supply coordinate names which include spaces.

>>> da.sel({'Set Magnetic Field':slice(131, 154, None)})
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 19, Frequency: 1001)>
array([[0.446916, 0.448087, 0.446013, ..., 0.315432, 0.280684, 0.244377],
       [0.364744, 0.371938, 0.377282, ..., 0.315766, 0.280974, 0.244608],
       [0.364957, 0.364845, 0.359775, ..., 0.316024, 0.281234, 0.244815],
       ...,
       [0.457339, 0.45351 , 0.447263, ..., 0.328263, 0.29388 , 0.257623],
       [0.457564, 0.453792, 0.447533, ..., 0.332801, 0.298602, 0.262485],
       [0.457725, 0.454055, 0.447757, ..., 0.340996, 0.307394, 0.271574]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 131.2 132.5 ... 152.5 153.8
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
Attributes:
    units:

Instead of using slices you can also select a single value. For this you may use ``method='nearest'`` as an additional *kwarg*.

>>> da.sel({'Set Magnetic Field':131}, method='nearest')
<xarray.DataArray 'Im_S11' (Frequency: 1001)>
array([0.446916, 0.448087, 0.446013, ..., 0.315432, 0.280684, 0.244377])
Coordinates:
    Set Magnetic Field  float64 131.2
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
Attributes:
    units:

Please note, that in this case the asterisk in front of the selected coordinate axis vanishes and the ``Set Magnetic Field`` have both vanished.
This dimension can not be used in further selection. This operation has decreased the dimensionality of the data under review.
Though multiple selections can be supplied in one call of the ``.sel`` method
(e.g. ``{'Set Magnetic Field':slice(131, 154, None), 'Frequency': slice(5.6e3, 5.8e3, None)}``, slicing and nearest can not be used in the same call.

The ``.isel`` method works almost identical, just that it does not select the *value* of a coordinate axis, but the
index number.

Math and Computation
--------------------

Numpy-like Math
^^^^^^^^^^^^^^^

When it comes to basic math, in most cases xarrays behave like numpy arrays.

>>> absolute = np.abs(d['Re_S11']+1j*d['Im_S11'])
>>> absolute
<xarray.DataArray (Set Magnetic Field: 21, Frequency: 1001)>
array([[0.45335944, 0.44938621, 0.445825  , ..., 0.50342391, 0.50166236,
        0.50006694],
       [0.45351756, 0.4495329 , 0.44601454, ..., 0.50387743, 0.50214325,
        0.50055285],
       [0.38165301, 0.38052807, 0.38066123, ..., 0.50430498, 0.50254997,
        0.50097015],
       ...,
       [0.45800198, 0.45426767, 0.45122987, ..., 0.50852291, 0.50671766,
        0.50504445],
       [0.45813408, 0.45450447, 0.45141898, ..., 0.50857588, 0.50686357,
        0.50521018],
       [0.45839378, 0.45471707, 0.45162554, ..., 0.50417154, 0.50328084,
        0.50203811]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03

Broadcasting
""""""""""""

One major difference is how the so-called *broadcasting* is handled. Broadcasting is procedure which is used to do math on
arrays with different dimensionalities. A simple example would be the addition of a scalar value to a 1D array. However,
this procedure can also be used to combine shapes such as ``(4, 100, 256)`` and ``(4, 100)``. In numpy, broadcasting works
simply via the order of the dimensions. In xarray, it will broadcast dimensions with the same dimension name to each other.
While this is very comfortable to use in most cases, it can cause problems, when non equivalent are accidentally given the same name.

Xarray Convenience Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

xarray offers several easy to use features, such as differentiation along an axis ``diff = da.differentiate('Frequency')``,
summation or averaging along an axis ``s = da.sum('Frequency')``, ``avg = da.mean('Frequency')``. This is particularly
powerful, since it can be combined with selection. For example the average of a specified frequency range:

>>> da.sel(Frequency=slice(5.6e3, 5.8e3)).mean('Frequency')
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 21)>
array([-0.01415238, -0.01310859, -0.01218391, -0.01642724, -0.01769279,
       -0.0174761 , -0.01850722, -0.02077479, -0.02052241, -0.01970442,
       -0.01889676, -0.01832782, -0.01798551, -0.01778508, -0.01764641,
       -0.01754683, -0.01746456, -0.01738205, -0.01731453, -0.0172626 ,
       -0.01721515])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0

``.min()``, ``.max()`` can compute minimum and maximum values of an array (along a desired axis), while ``.idxmin()``,
``.idxmax()`` compute the coordinate labels at which these are found.

Masking Arrays
""""""""""""""

Data selection only works along the cartesian coordinates of the data under investigation. In some situations, however,
it is necessary to exclude some data according to some other criterion. This could mean dropping all values above a
certain value or only selecting values inside a circle of 2D DataArray with x, y coordinates. The
``xarray.Dataarray.where``-method allows for the selection of data on the basis of a boolean map, e.g. ``da>0.4``.
All entries of the DataArray, which do not satisfy this condition, will be viewed as *nan* which means not a number.
These conditions can also be combined by using python bitwise operators ``&`` (AND), ``|`` (OR), ``^`` (XOR) , ``~`` (NOT)
and can utilize every data source such as coordinates or other data variables, as long as they can be broadcasted together.

>>> da.where((da>0.4) & (da<0.447))
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 21, Frequency: 1001)>
array([[       nan,        nan, 0.44543207, ...,        nan,        nan,
               nan],
       [0.44691569,        nan, 0.44601342, ...,        nan,        nan,
               nan],
       [       nan,        nan,        nan, ...,        nan,        nan,
               nan],
       ...,
       [       nan,        nan,        nan, ...,        nan,        nan,
               nan],
       [       nan,        nan,        nan, ...,        nan,        nan,
               nan],
       [       nan,        nan,        nan, ...,        nan,        nan,
               nan]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
Attributes:
    units:

This technique can be quite helpful in order to filter data, for instance by only considering data close to a certain
feature in summation. The advantage here is, that it can easily be parametrized as opposed to ``.sel``

Manipulating the underlying Numpy Array
"""""""""""""""""""""""""""""""""""""""

Sometimes, it can be helpful to just drop the labeled axis. You can access the underlying numpy array by calling.

>>> nd_array = da.to_numpy()

The other way round, you can manipulate the contents of a DataArray by using:

>>> da.data = nd_array * 5

While this technique can be useful, sometimes, in this particular case, it would have the same result as:

>>> da = da * 5

Alternatively, you can work with a (deep) copy:

>>> new_da = da.copy(data=nd_array-25, deep=True)

You can also manipulate coordinates. This overwrites the values of Frequency coordinate label array:

>>> da['Frequency'] = da['Frequency'] * 5

Or you can create a new coordinate axis along Frequency:

>>> da.assign_coords({'double frequency': ('Frequency', da['Frequency'].to_numpy()*2)})
<xarray.DataArray 'Im_S11' (Set Magnetic Field: 21, Frequency: 1001)>
array([[0.449762, 0.449024, 0.445432, ..., 0.315165, 0.280422, 0.244154],
       [0.446916, 0.448087, 0.446013, ..., 0.315432, 0.280684, 0.244377],
       [0.364744, 0.371938, 0.377282, ..., 0.315766, 0.280974, 0.244608],
       ...,
       [0.457564, 0.453792, 0.447533, ..., 0.332801, 0.298602, 0.262485],
       [0.457725, 0.454055, 0.447757, ..., 0.340996, 0.307394, 0.271574],
       [0.457942, 0.454288, 0.447996, ..., 0.364995, 0.332711, 0.298152]])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
  * Frequency           (Frequency) float64 5.65e+03 5.651e+03 ... 6.35e+03
    double frequency    (Frequency) float64 1.13e+04 1.13e+04 ... 1.27e+04
Attributes:
    units:

This syntax can even be used to create 2D coordinates (e.g. radius as a function of x and y, or as in this case the *nonsensical* sum of both coordinates).

.. code-block:: python

   import numpy as np
   import xarray as xr
   f = da['Frequency'].to_numpy()
   b = da['Set Magnetic Field'].to_numpy()
   F, B = np.meshgrid(f, b, indexing='ij')
   R = F + B
   da = da.assign_coords(R=(('Frequency', 'Set Magnetic Field'), R))

Fitting
-------

``xarray.DataArray.polyfit`` can be used for quick polynomial fitting. This snippet calculates the slope (degree=1) along the
*Frequency* axis.

>>> da.polyfit('Frequency', 1)['polyfit_coefficients'].sel(degree=1)
<xarray.DataArray 'polyfit_coefficients' (Set Magnetic Field: 21)>
array([-1.01552749e-04, -1.00840547e-04, -9.38317778e-05, -9.36537903e-05,
       -9.70468779e-05, -9.99572567e-05, -1.01713737e-04, -1.02445728e-04,
       -1.02751882e-04, -1.02915830e-04, -1.02997863e-04, -1.03150440e-04,
       -1.03228815e-04, -1.03372508e-04, -1.03522292e-04, -1.03731269e-04,
       -1.03966911e-04, -1.04177855e-04, -1.04534305e-04, -1.05104657e-04,
       -1.06324887e-04])
Coordinates:
  * Set Magnetic Field  (Set Magnetic Field) float64 130.0 131.2 ... 153.8 155.0
    degree              int32 1

For more elaborate models ``xarray.DataArray.curvefit`` can be used. However, this exceeds the scope of this tutorial.

Interpolation
-------------

xarray offers a convenient interpolation method ``xarray.DataArray.interp``. Interpolate works especially easy by supplying
DataArrays as input.

.. code-block:: python

   new_frequency = np.linspace(float(da['Frequency'].min()), float(da['Frequency'].max()), 4)
   new_frequency = xr.DataArray(new_frequency, dims=('New Frequency'), coords={'New Frequency': new_frequency})
   interpolated_data = da.interp(Frequency=new_frequency)
   print(interpolated_data.isel({'Set Magnetic Field': 0}))

Will result in:

.. code-block:: console

   <xarray.DataArray 'Re_S11' (New Frequency: 4)>
   array([-0.05700159, -0.53417212,  0.1511845 ,  0.43641236])
   Coordinates:
       Set Magnetic Field  float64 130.0
       Frequency           (New Frequency) float64 5.65e+03 5.883e+03 ... 6.35e+03
     * New Frequency       (New Frequency) float64 5.65e+03 5.883e+03 ... 6.35e+03
   Attributes:
       units:

This can also be used as a means of coordinate transformation. AS you can see in the above example, the coordinate
dimension has changed from *Frequency* in the original DataArray to *New Frequency*, the dimension name as supplied by
the new_frequency DataArray. The *value* of new_frequency marks the value *for that coordinate* in the *old*
coordinate system. In the above example both are equal. On the other hand you can as well construct something like this:

.. code-block:: python

   new_frequency = np.linspace(float(da['Frequency'].min()), float(da['Frequency'].max()), 4)
   unit_conversion = xr.DataArray(new_frequency, dims=('New Frequency'), coords={'New Frequency': new_frequency/1000})
   interpolated_data = da.interp(Frequency=unit_conversion)
   print(interpolated_data.isel({'Set Magnetic Field': 0}))

Here, the coordinate axis has been simultaneously divided by a factor of 1000. This gets particularly interesting in the
case of 2D interpolation.

In this case, you can specify an array on a grid in a new coordinate system, whose values contain the coordinates in the
old coordinate system. The interpolation then performs a lookup operation for each point of the grid in the new
coordinate system and fills it with corresponding values of the old coordinate system at the specified position.

This code snipped transforms an array which is filled in polar coordinates into data in cartesian coordinates.

.. code-block:: python

   kx = np.linspace(-k_edge//mod, k_edge//mod, 30+1)
   ky = np.linspace(-k_edge//mod, k_edge//mod, 30+1)

   KX, KY = np.meshgrid(kx, ky, indexing='ij')

   angle_new = xr.DataArray(np.arctan2(KX, KY)*180/np.pi, dims=('kx', 'ky'), coords={'kx': kx, 'ky': ky})
   k_new = xr.DataArray(np.sqrt(KX**2+KY**2), dims=('kx', 'ky'), coords={'kx': kx, 'ky': ky})
   polate = disp.interp(theta=angle_new, k=k_new)

Plotting
--------

``xarray`` offers a powerful interface for ``matplotlib``. Plots can be generated by calling the
``xarray.DataArra.plot`` method. It will try to infer the kind of plot best suited for a given array shape.

>>> da.plot()

In the case of 2D data, this will result in a colormap.

In order to specify the shape of a plot in more detail, the plot can be created by calling one of
``xarray.DataArray.plot.line``, ``xarray.DataArray.plot.scatter``, ``xarray.DataArray.plot.imshow``,
``xarray.DataArray.plot.pcolormesh``. For instance the same data can be plotted as:

>>> da.plot.line(hue='Set Magnetic Field')

In this particular example, the data will be shown as a line plot, where each slice along *Set Magnetic Field* is given a different color.

If you want to see, what each of these plot types look like, please check the `xarray plotting section <https://docs.xarray.dev/en/stable/user-guide/plotting.html>`_.

However, as a quick start, it helps to know, that in the xarray interface to matplotlib, dimension names can be supplied
to the plotting function, to give that dimension a certain function in the plot.

+-----------------------------------+---------------------------------+
|``x``                              |Use coordinate as x-axis         |
+-----------------------------------+---------------------------------+
|``y``                              |Use coordinate as y-axis         |
+-----------------------------------+---------------------------------+
|``hue``                            |Change line color                |
+-----------------------------------+---------------------------------+
|``col``                            |Distribute along subplot columns |
+-----------------------------------+---------------------------------+
|``row``                            |Distribute along subplot rows    |
+-----------------------------------+---------------------------------+

The last two keywords are particularly interesting, since they can be used to generate multiple panels in a grid
arangement order. This is very helpful to get a hold of large amounts of data on one glance.

You can also use the ``ax`` keyword to assign a plot to a previously generated matplotlib axis. This can be very helpful
if you are using the object oriented matplotlib interface.

