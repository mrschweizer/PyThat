import h5py
import numpy as np
import pathlib as pl
import textwrap
import xarray as xr
import json
import yaml
# import os
# import io


class MeasurementTree:
    def __init__(self, filepath, index=True, override: bool = False, chunk=None, keep_file_open=False):
        """
        :param filepath: r-string that points to h5 file
        :param index: optional: tuple that describes group number and group internal number
        :param chunk: None will skip chunking before saving, True will set chunks to 'auto', dict will forward dict to xarray.Dataset.chunk call
        :param keep_file: If False (default), the file will be closed after conversion.
        """
        self.filepath = filepath
        self.path = pl.Path(filepath).absolute()
        print(self.path)
        self.f = h5py.File(self.path, 'r+')
        self.definition = []
        self.tree = [[]]
        self.indent_max = 0
        self.new_tree = []
        self.chunk = chunk
        self.target = None
        self.shape = None
        self.data = None
        self.data_scales = None
        self.array: xr.DataArray or None = None
        self.index: tuple or None = index
        self.indicator_name = None
        self.save_path: None or pl.Path = None
        self.tree_string = None
        self.labbook = None
        self.devices = None
        self.logs = None
        self.dataset = None
        self.metadata = {}
        self.attrs = None
        self.eLab_meta = None

        if not override:
            try:
                self.open_netcdf()
            except AttributeError:
                self.construct_tree()
                if not index:
                    return
                self.save_netcdf()
            except FileNotFoundError:
                self.construct_tree()
                if not index:
                    return
                self.save_netcdf()
        else:
            self.construct_tree()
            if index is False:
                return
            self.save_netcdf()
        if not keep_file_open:
            self.f.close()

    def list_hdf5(self):
        print(self.f.visit(print))

    @staticmethod
    def save_file_from_string(obj, path):
        try:
            obj.to_netcdf(path)
        except PermissionError:
            obj.to_netcdf(str(path).encode('UTF-8'))

    def save_netcdf(self):
        self.array: xr.DataArray
        if self.index is not True:
            name = self.path.with_suffix('').name + str(self.index)
            print(f'Index: {self.index}')
            self.save_path = self.path.with_name(name).with_suffix('.nc').absolute()
        else:
            self.save_path = self.path.with_suffix('.nc').absolute()
        if self.dataset is not None:
            if self.chunk is not None:
                if isinstance(self.dataset, dict):
                    self.dataset = self.dataset.chunk(**self.chunk)
                elif self.chunk is True:
                    self.dataset = self.dataset.chunk(chunks='auto')
            self.save_file_from_string(self.dataset, self.save_path)
            print('Saved dataset as {}'.format(self.save_path))
        elif self.array is not None:
            self.save_file_from_string(self.dataset, self.save_path)
            print('Saved as {}'.format(self.save_path))

    def open_netcdf(self):
        """This function opens the expected output netcdf if it exists.\n
        Otherwise save_netcdf() is called to create such a file."""

        if self.index is True:
            try:
                self.save_path = self.path.with_suffix('.nc').absolute()
                self.dataset = xr.open_dataset(self.save_path)
                print(f'Successfully loaded {self.save_path}')
            except FileNotFoundError:
                print('File not found')
                self.save_netcdf()
                self.dataset = xr.open_dataset(self.save_path)
        elif self.index is None:
            raise FileNotFoundError
        elif self.index is not False:
            try:
                name = self.path.with_suffix('').name + str(self.index)
                self.save_path = self.path.with_name(name).with_suffix('.nc').absolute()
                self.array = xr.open_dataarray(self.save_path)
                self.dataset = xr.open_dataarray(self.save_path)
            except FileNotFoundError:
                self.save_netcdf()
                self.array = xr.open_dataarray(self.save_path)
                self.dataset = xr.open_dataarray(self.save_path)
        try:
            self.devices = json.loads(self.dataset.attrs['devices'])
            self.labbook = json.loads(self.dataset.attrs['labbook'])
            self.logs = json.loads(self.dataset.attrs['logs'])
            self.definition = json.loads(self.dataset.attrs['scan_definition'])
            self.tree_string = json.loads(self.dataset.attrs['measurement_tree'])
            self.attrs = {'devices': self.devices,
                          'labbook': self.labbook,
                          'logs': self.logs,
                          'measurement_tree': self.tree_string,
                          'scan_definition': self.definition}
        except KeyError:
            print('Metadata not found. It will not be available.')

    def construct_tree(self):
        self.definition = {self.check_for_sp_char(i): self.convert_to_dict(k) for (i, k) in self.f['scan_definition'].items()}
        if 'tree_view' in self.definition.keys():
            del(self.definition['tree_view'])
        self.devices = {self.check_for_sp_char(i): self.convert_to_dict(k, truncate=True) for (i, k) in self.f['devices'].items()}
        self.labbook = {self.check_for_sp_char(i): self.convert_to_dict(k) for (i, k) in self.f['labbook'].items()}
        self.logs = self.convert_to_dict(self.f['measurement/log'])
        self.eLab_meta = self.get_elab_attrs()
        """
        ////////////////////////////////////////////////////////
        This reconstructs the multidimensional measurement tree.
        ////////////////////////////////////////////////////////
        """
        # Get a list of rows names
        rows = list(self.definition)
        """
        # Sort rows for indentation
        indent_list = sorted(self.definition, key=lambda z: self.definition[z]['tree indent level'], reverse=True)
        """

        # The first step should be grouping adjacent rows with the same tree indent level
        # Initialize the indentation
        self.new_tree = [Group(self)]
        previous_indent = int(self.definition[rows[0]]['tree indent level'])
        for row, value in self.definition.items():
            # Get indentation level of item
            new_indent = int(value['tree indent level'])
            # Entries with same indentation go to the same group
            if new_indent == previous_indent:
                self.new_tree[-1].group_entries[row] = value
            # Entries which create a new group for new indentation
            elif new_indent > previous_indent:
                self.indent_max = max(self.indent_max, new_indent)
                self.new_tree.append(Group(self))
                self.new_tree[-1].group_entries[row] = value
                self.new_tree[-1].tree_indent = new_indent

                # Add next to last group as parent group
                self.new_tree[-1].parent_group = self.new_tree[-2]
                # Add last key of parent group as parent row
                self.new_tree[-1].parent_row = list(self.new_tree[-2].group_entries.keys())[-1]
            # Case of declining tree
            else:
                self.new_tree.append(Group(self))
                self.new_tree[-1].group_entries[row] = value
                self.new_tree[-1].tree_indent = new_indent

                # Trace back to parent
                red_list = list(filter(lambda x: x.tree_indent < new_indent, self.new_tree))
                try:
                    self.new_tree[-1].parent_group = red_list[-1]
                    self.new_tree[-1].parent_row = list(red_list[-1].group_entries.keys())[-1]
                except IndexError:
                    print('Expected behaviour: Last group does not have a parent.')

            previous_indent = new_indent

        # Assemble siblings
        # These are groups which depend on the same parent row
        print('Number of groups: {}'.format(len(self.new_tree)))
        # Compare tree_indent levels of all element pairs
        for i, k in enumerate(self.new_tree):
            # siblings.append(k)
            for q, j in enumerate(self.new_tree[i+1:None]):
                # If the tree_indent subverts the initial level, the two entries are not really connected
                if j.tree_indent < k.tree_indent:
                    break
                # Add both entries to the siblings property.
                if j.tree_indent == k.tree_indent:
                    j.siblings.append(k)
                    k.siblings.append(j)

        """List Measurement Tree"""
        print_tree_list = []
        possible_indicators = []
        for group, j in enumerate(self.new_tree):
            for row, (i, k) in enumerate(j.group_entries.items()):
                properties = ['function',
                              'device name',
                              'control name',
                              'start', 'stop',
                              'steps',
                              'waiting period (ms)',
                              'repetitions',
                              'value']
                values = []
                printout = f'({group}, {row}) "{i}": '
                for name in properties:
                    try:
                        values.append(k[name])
                    except KeyError:
                        pass
                try:
                    if k['function'] in ['indicator', 'internal - numeric input']:
                        possible_indicators.append((group, row))
                except KeyError:
                    pass
                printout += str(values)
                try:
                    printout += ' ' + str(self.get_data(i).shape)
                except KeyError:
                    pass
                line = textwrap.indent(printout, ' '*2*int(j.tree_indent))
                print_tree_list.append(line)
                # print(line)
        self.tree_string = '\n'.join(print_tree_list)

        """User Input Index"""
        if self.index is None:
            # Get and parse user input for group and entry for self.target and self.index
            print("Please enter the Group number and the group internal number.")
            x = (0, 0)
            for i in range(3):
                inp = input()
                if inp == 'All':
                    break
                else:
                    try:
                        possible_indicators = [tuple([int(q) for q in inp.split(',')])]
                        break
                    except ValueError:
                        print("Input must be two integers, separated by a comma or 'All'.")
                        x = (0, 0)
        elif self.index is False:
            return
        elif self.index is True:
            pass
        else:
            # override possible_indicators, if index is specified
            possible_indicators = [self.index]
            print(f'Only one index selected: {possible_indicators[0]}')

        # create array with all core-data names
        # create self.metadata
        core_data_names = []
        for (i, k) in self.f['scan_definition'].items():
            meta_entry = self.get_metadata(i)
            if meta_entry is not None:
                try:
                    name_entry = meta_entry['name']
                    if isinstance(name_entry, list):
                        name = [self.avoid_duplicate(i, core_data_names) for i in name_entry]
                        meta_entry['name'] = name
                        core_data_names = core_data_names + name
                    elif isinstance(name_entry, str):
                        name = self.avoid_duplicate(name_entry, core_data_names)
                        core_data_names.append(name)
                        meta_entry['name'] = name
                except KeyError:
                    pass
            self.metadata[i] = meta_entry
        print(f'Core data names: {core_data_names}')

        # print()
        # print('Core Data Metadata:')
        # for i, j in self.metadata.items():
        #     if j is not None:
        #         print(i)
        #         for k in j.values():
        #             print(k)

        # Check control names in self.definition for duplicate and rename
        # control_keys: list of already encountered keys
        control_keys = core_data_names
        for v, u in self.definition.items():
            key_control_name = None
            try:
                key_control_name = u['control name']
            except KeyError:
                if u['function'] == 'internal - repetitions':
                    key_control_name = 'repetitions'
            # if key_control_name was not yet encountered, add to list of encountered keys
            # only if control key is either control name or repetitions
            if key_control_name is not None:
                key_control_name, unit = self.get_units(key_control_name)
                if key_control_name in control_keys:
                    key_control_name = self.avoid_duplicate(key_control_name, control_keys)
                u['control name'] = key_control_name
                control_keys.append(key_control_name)
                u['units'] = unit
            # print(u)
        # print([u['units'] for u in self.definition.values() if 'units' in u])

        all_indicators = []
        for x in possible_indicators:
            # self.index = x
            group, row = x
            # self.index = x
            self.target: Group = self.new_tree[group]

            try:
                self.data = self.target.get_data(row)
            except KeyError:
                print(f'Data for {x} could not be found.')
                continue
            data_shape = tuple(list(self.data.shape)[1:])
            parent: Group = self.target.parent_group
            parent_row = self.target.parent_row

            global_row = self.target[row][0]

            try:
                self.indicator_name = self.definition[global_row]['control name']
            except KeyError:
                if self.definition[global_row]['function'] == 'internal - numeric input':
                    self.indicator_name = self.definition[global_row]['name']
                else:
                    raise KeyError(f'Error while trying to fetch the name for an numeric input in {global_row}')
            print()
            print("Building xarray object for:")
            print(f"{self.indicator_name}, {global_row}")
            print("________________________________________________________")

            """
            Go through all parents and add control names to dimension names.
            """
            coords = {}
            shape = []
            units = []
            segments = []

            while parent is not None:
                try:
                    control_name = self.definition[parent_row]["control name"]
                except KeyError as key:
                    pass

                try:
                    unit = self.definition[parent_row]["units"]
                except KeyError:
                    print(f'No Unit found for {control_name}, {parent_row}')
                """check if unit has already been stored"""

                # Get units from paranthesis in control name
                control_name, _ = self.get_units(control_name)
                # if self.definition[parent_row]['function'] in ['scalar control']:

                row_data = None
                roi = None
                try:
                    row_data = parent.get_data()
                    # Add shape of dimension to shape list
                    shape.append(row_data.shape[0])
                    roi = [len(row_data)]
                    # Add control name as key to the coords dict. Assign data to that key.
                except KeyError as err:
                    if self.definition[parent_row]['function'] == 'internal - repetitions':
                        print('Repetitions. Generating incrementing as coords.')
                        rep = int(self.definition[parent_row]['repetitions'])
                        roi = [rep]
                        shape.append(rep)
                        row_data = np.arange(rep)
                    elif self.definition[parent_row]['function'] == 'scalar control':
                        print(f'Scalar control {control_name} without data. Generating coords.')
                        if isinstance(self.definition[parent_row]['start'], list):
                            part = []
                            roi = []
                            # TODO: Find a way to save ste for later use. Save list of steps in array.
                            for sta, sto, ste, eq in zip(self.definition[parent_row]['start'],
                                                         self.definition[parent_row]['stop'],
                                                         self.definition[parent_row]['steps'],
                                                         self.definition[parent_row]['equation']):
                                part.append(np.linspace(sta, sto, int(ste)))
                                roi.append(int(ste))
                                row_data = np.concatenate(part)
                        else:
                            roi = [int(self.definition[parent_row]['steps'])]
                            row_data = np.linspace(self.definition[parent_row]['start'],
                                                   self.definition[parent_row]['stop'],
                                                   int(self.definition[parent_row]['steps']))
                        try:
                            shape.append(int(self.definition[parent_row]['steps']))
                        except TypeError:
                            shape.append(int(np.sum(self.definition[parent_row]['steps'])))
                if row_data is not None:
                    coords[control_name] = row_data
                    units.append(unit)
                    if roi is not None:
                        segments.append(roi)
                parent_row = parent.parent_row
                parent = parent.parent_group

            dims = list(coords.keys())
            units.reverse()
            dims.reverse()
            segments.reverse()

            self.indicator_name, indicator_unit = self.get_units(self.indicator_name)

            # iterate over metadata to innermost data to get names of all dimensions
            metadata = self.metadata[self.target[row][0]]
            if metadata is not None:
                print(f'Get Metadata for: {self.target[row][0]}')
                for i in range(len(data_shape)):
                    coord_name = metadata['name'][i]
                    scales = self.get_scales(self.target[row][0], i)
                    coords[coord_name] = scales
                    dims.append(coord_name)
                    segments.append([len(scales)])
                    unit = metadata['unit'][i]
                    units.append(unit)
            else:
                print(f'No Metadata found for {self.indicator_name}')
                coord_name = 'some_dimension'
                for i, dat_shape in enumerate(data_shape):
                    coord_name = self.avoid_duplicate(coord_name, coords.keys())
                    coords[coord_name] = np.arange(dat_shape)
                    segments.append(float('nan'))
                    dims.append(coord_name)
                    units.append('')

            dims = tuple(dims)
            shape.reverse()
            self.shape = tuple(shape)+data_shape
            try:
                self.data = np.reshape(self.data, self.shape)
                print(f'Desired shape: {self.shape}, data shape: {self.data.shape}, size: {self.data.size}')
            except ValueError:
                # TODO: Find a way to drop empty slices
                print('Measurement not finished?')
                print(f'Desired shape: {self.shape}, data shape: {self.data.shape}, size: {self.data.size}')
                flattened_length = np.prod(shape)
                flattened_length_data = self.data.shape[0]
                if not flattened_length_data == int(self.data.size/np.prod(data_shape)):
                    raise ValueError('The dimensions extracted from the measurement tree dont add up')
                print(f'Number of core measurements: {flattened_length_data} of {flattened_length}')
                flattened_shape = (flattened_length,)+data_shape
                print(f'flattened shape: {flattened_shape}')
                # initialize flattened with nan
                flattened_new = np.empty(flattened_shape)
                flattened_new[...] = np.nan
                # write existing override nans with existing data
                flattened_new[0:flattened_length_data, ...] = self.data
                # bring data to correct shape
                self.data = np.reshape(flattened_new, self.shape)


            print()
            self.array = xr.DataArray(self.data, dims=dims, coords=coords, name=self.indicator_name)
            # Add units to Attributes
            for x, y, z in zip(dims, units, segments):
                self.array[x].attrs['units'] = y
                self.array[x].attrs['segments'] = z
            self.array.attrs['units'] = indicator_unit
            all_indicators.append(self.array)
            print(f'Segments: {segments}')

        self.dataset = xr.combine_by_coords(all_indicators)

        # add metadata to xarray attrs
        try:
            self.attrs = {'devices': self.devices,
                          'labbook': self.labbook,
                          'logs': self.logs,
                          'measurement_tree': self.tree_string,
                          'scan_definition': self.definition}
        except NameError:
            print('Metadata has not been initialized.')
        from json import dumps
        for attr, val in self.attrs.items():
            self.dataset.attrs[attr] = dumps(val)

    def print_metadata(self, metadata):
        """
        Print additional metadata in yaml form.
        :param metadata: Can be {'devices', 'labbook', 'logs', 'scan_definition'}
        :return: None
        """
        print(yaml.dump(self.attrs[metadata]))

    @staticmethod
    def avoid_duplicate(init_name, lis):
        itera = 1
        init_name0 = init_name
        while init_name in lis:
            init_name = f'{init_name0}_{itera}'
            itera += 1
        return init_name

    @staticmethod
    def get_units(control_name):
        from re import compile, search
        find_units = compile(r' *\((.+)\) *')
        try:
            g = find_units.search(control_name)
            unit = g.group(1)
            rem = g.group(0)
            control_name = control_name.replace(rem, "").rstrip()
            return control_name, unit
        except AttributeError:
            return control_name, ''

    def get_scales(self, row: str, index: int) -> np.ndarray or None:
        scale_shape = (self.data.shape[0], (int(self.definition[row]['dimensions'])+1), 2)
        data_shape = self.data.shape[1:][index]
        try:
            scale_specs = np.array(self.f['measurement/' + row + '/scale']).reshape(scale_shape)[0, index, :]
            stop = data_shape*scale_specs[1] + scale_specs[0]
            scales = np.linspace(scale_specs[0], stop, data_shape)
            return scales
        except KeyError:
            print('No scales found.')
            return None
        except ValueError:
            print('Scales do not fit the required dimensions.')
            return np.arange(data_shape)

    def get_data(self, row: str):
        """
        :param row: Name of the row
        :return:
        """
        return self.f['measurement/' + row + '/data']

    def get_metadata(self, row: str, truncate: bool = False) -> np.ndarray or None:
        try:
            obj = self.f['measurement/' + row + '/metadata'].asstr()[:, :]
            metadata = {}
            for x in obj:
                metadata[x[0]] = []
            for x in obj:
                test_string = x[1][1:-1] if truncate else x[1]
                try:
                    z = float(test_string)
                except ValueError:
                    if test_string == 'false':
                        z = False
                    elif test_string == 'true':
                        z = True
                    else:
                        z = test_string
                metadata[x[0]].append(z)
            return metadata
        except KeyError:
            return None

    def get_elab_attrs(self, group: str = 'eLab') -> dict:
        group_dict = {}
        try:
            group_dict = {key: value for key, value in self.f[group].attrs.items()}
            for key, value in group_dict.items():
                try:
                    group_dict[key] = value
                except KeyError:
                    pass
        except KeyError:
            print('The eLab Group could not be found in the hdf5 file.')
        return group_dict

    @staticmethod
    def check_for_sp_char(text):
        import re
        special_char = re.compile(r"%%%(\d+)%%%")
        text = str(text)
        res = special_char.finditer(text)
        for v in res:
            text = text.replace(v.group(), chr(int(v.group(1))))
        return text

    @staticmethod
    def convert_to_dict(obj: h5py.Dataset, truncate=False):
        """This function takes data sets as saved by thatec os and converts them into dictionaries.
        Works for filetype '|o'
        :parameter obj: dataset object which should be converted
        :parameter truncate: bool, defines if '[]' will be cut
        """
        if not isinstance(obj, h5py.Dataset):
            return {}
        """Problem: In den Thatec Daten gibt es teils metadaten in denen die gleichen Keys mehrmals vorkommen.
        Dies führt dazu, dass diese überschrieben werden."""
        a = {}
        for i, x in enumerate(obj.asstr()[:, :]):
            test_string = x[1][1:-1] if truncate else x[1]
            try:
                z = float(test_string)
            except ValueError:
                if test_string == 'false':
                    z = False
                elif test_string == 'true':
                    z = True
                else:
                    z = MeasurementTree.check_for_sp_char(test_string)
            key = MeasurementTree.check_for_sp_char(x[0])
            try:
                # Check if entry exists
                q = a[key]
                # If not already, make it a list
                if not isinstance(q, list):
                    q = [q]
                # Append new entry to said list
                q.append(z)
                a[key] = q
            except KeyError:
                # If it doesn't exist, create entry
                a[key] = z
        return a


class Group:
    def __init__(self, m_tree: MeasurementTree):
        self.parent_group: Group or None = None
        self.parent_row = None
        self.tree_indent = 0
        self.group_entries: dict = {}
        self.siblings = []
        self.max_indent = 0
        self.m_tree = m_tree

    def __getitem__(self, index: int):
        return list(self.group_entries.items())[index]

    def get_data(self, index: int = -1):
        """Get data of indexed entry of that group.
        :param index: Specified index in that group. Last index by default.
        :return: The data set of 'measurement/*row*/data' of the specified index"""
        row = list(self.group_entries.keys())[index]
        return self.m_tree.f['measurement/' + row + '/data']

    def __repr__(self):
        return str(self.group_entries.keys())


class Row:
    def __init__(self):
        self.group = None
        self.parent = None
        self.name: str or None = None


def consolidate_dims(array, name_includes, compare_to: str or None = None, new_dim: str = None):
    """
    This function helps finding unnecessary duplicates of dimensions.
    :param array: The xarry object which is to be changed.
    :param name_includes: String which must be included in the dimension name or list of dimension names which should be merged.
    :param compare_to: String or None: The equality of this coordinate axis with all other axis is a condition for
    merging. Defaults to the first coordinate which satisfies name_includes.
    :param new_dim: Name which will be given to the merged dimension. Defaults to compare_to
    :return: xarray object where dimension and coordinate duplicates have been dropped.
    """

    print("Assuming all given coordinates do have the same values.")
    candidates = []
    # find candidates which satisfy name_includes
    if isinstance(name_includes, str):
        for x in array.dims:
            if name_includes in x:
                candidates.append(x)
    elif isinstance(name_includes, list):
        candidates = name_includes
    candidates_backup = candidates.copy()
    compare_to_backup = compare_to
    new_dim_backup = new_dim
    for test in candidates_backup:
        candidates = candidates_backup.copy()
        compare_to = compare_to_backup
        new_dim = new_dim_backup
        # initialize compare to
        if compare_to is None:
            compare_to = test
        elif compare_to in candidates:
            pass
        else:
            raise KeyError("compare_to argument not found in selected dimensions")
        candidates.remove(compare_to)
        # initialize new_dim
        if new_dim is None:
            new_dim = compare_to
        # initialize list of identical candidates
        identicals_list = [compare_to]
        temp = array[compare_to].data
        # check if all axis are identical to temp
        for dim_name in candidates:
            if np.array_equal(array[dim_name].data, temp):
                identicals_list.append(dim_name)
        if len(identicals_list)>1:
            print(f'Duplicate coordinates found:\n{identicals_list}')
            break
    if not len(identicals_list)>1:
        raise ValueError("No duplicate coordinate axis found. Try using the 'compare_to' argument.")
    from string import ascii_letters, digits
    from random import choices
    temp_name = "".join(choices(ascii_letters+digits, k=16))
    for dim_name in identicals_list:
        array = array.swap_dims({dim_name: temp_name})
    array = array.assign_coords({temp_name: temp})
    array = array.drop_vars(identicals_list)
    array = array.rename_dims({temp_name: new_dim})
    array = array.rename({temp_name: new_dim})
    return array


# Add consolidate dims as methods to xarray.DataArray and xarray.Dataset
xr.DataArray.consolidate_dims = consolidate_dims
xr.Dataset.consolidate_dims = consolidate_dims
