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
The package reconstructs the measurement tree and lets the user choose the row containing an indicator. It then uses the metadata from the measurement tree to construct an xarray object with n+m dimensions, where n is the dimension of the indicator in the specified row and m the number of indents/loops.

Since xarray is built around labeled arrays, it also reconstructs the dimension label (dims) and label coordinate (coords) attributes of the xarray objects. The scope of PyThat is the conversion into the xarray format. For use of xarray see the well maintained `xarray documentation <https://docs.xarray.dev/en/stable/user-guide/index.html>`_.

After starting at version 0.27 all data is read for all valid indicators and combined to a dataset. The old version with indexing should still work, however.



Examples
========

Load Data
---------
.. code-block:: python

   from PyThat import MeasurementTree
   path = r'C:\some_folder\measurement_file.h5'
   mt = MeasurementTree(path)

The result will look like this:

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

Indicator rows have been translated to data variables (e.g. Im_S11) and controls to coordinates (e.g. "Set Magnetic Field").
Since Im_S11 etc. are 1D data, they have also been assigned a frequency coordinate. The coordinate names have been altered,
so that they are unique, in order to prevent different devices/functions having the same coordinate name.
