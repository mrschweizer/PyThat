API Reference
=============


.. py:class:: PyThat.MeasurementTree(path, override=False, index=True)

   Return a list of random ingredients as strings.

   :param path: Path to .h5 measurement file. Can be relative or absolute path.
   :type kind: str
   :param override: This will force PyThat to reconstruct the measurement tree again, even if there is already a netcdf
                    file (.nc) from a previous run. Setting this to True is the only way to ensure that most attributes
                    are available during a run.
   :type overide: bool
   :param index: Default True: All of the measurement data being loaded into a xarray Dataset.

                 Tuple: DataArray of that particular group.

                 None: User input after the measurement tree has been printed.

                 False: Exit after measurement tree has been printed.
   :type index: bool, tuple (i, j) or None

   .. py:attribute:: dataset

      :type: xarray.Dataset

      If index is True, all available data will be included here.


   .. py:attribute:: array

      :type: xarray.DataArray

      If index is None or Tuple, the data from the selected row will be included here.


   .. py:attribute:: path

      :type: pathlib.Path

      Absolute path to h5 file


   .. py:attribute:: filepath

      :type: str

      String representation of the filepath as entered by user.

   .. py:attribute:: index

      :type: Bool, tuple or None

      Index of data which will be read during construct_tree. Will iterate through all relevant rows if True.

   .. py:attribute:: f

      :type: h5py.File

      File handler of the .h5 file.

   .. py:attribute:: save_path

      :type: None or pathlib.Path

      Path to the generated netcdf (.nc) file.

   .. py:attribute:: definition

      :type: dict

      Scan definition/measurement tree of the measurement as saved by THATec without any processing.

   .. py:attribute:: tree_string

      :type: str

      String representation of the scan definition/measurement tree.

   .. py:attribute:: labbook

      :type: dict

      Contains labbook entries as specified in Thatec interface.

   .. py:attribute:: devices

      :type: dict

      Contains devices configuration at beginning of measurement.

   .. py:attribute:: logs

      :type: dict

      Contains log entries which occured during the measurement.

   .. py:attribute:: metadata

      :type: dict

      Contains measurement metadata such as date and operator as specified in Thatec interface.

   .. py:method:: construct_tree()

      Goes through scan definition and reconstructs data in .h5 file. Is automatically called on creation of object.

   .. py:method:: open_netcdf()

      Open netcdf file from savepath.

   .. py:method:: save_netcdf()

      Save array to netcdf file at savepath.

   .. py:method:: save_netcdf_dset()

      Save dataset to netcdf file at savepath.

.. py:class:: PyThat.Group(m_tree: PyThat.MeasurementTree)

   Helper class for organizing measurement tree.