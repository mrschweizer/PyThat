import matplotlib.gridspec
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from matplotlib.widgets import TextBox
from pickle import dump, load
from matplotlib.widgets import RadioButtons
from xarray import DataArray
from xarray import Dataset
from xarray import broadcast
from xarray import merge
import xarray as xr

def load_record(path='ROI.sl'):
    with open(path, 'rb') as f:
        regions = load(f)
        return regions

def reduce_ds(ds, hyper_slice, remaining_dims):
    red_slice = hyper_slice.copy()
    for i in remaining_dims:
        del (red_slice[i])
    for x in red_slice.keys():
        if x in ds.coords.keys():
            ds = ds.sel({x: red_slice[x]})
        else:
            ds = ds.isel({x: red_slice[x]})
    da = ds.mean(list(red_slice.keys()))
    return da

def broadcast_ds(ds):
    return merge(broadcast(*[ds[var] for var in ds.data_vars.keys()]))

class SlicePlot1D:
    def __init__(self, da, dim, update_method, orientation, var=None, plot_kwargs=None):
        if plot_kwargs is not None:
            self.plot_kwargs = plot_kwargs.copy()
        else:
            self.plot_kwargs = {}
        self.var = var
        if isinstance(da, DataArray):
            self.mode = 'da'
            self.da = da
        elif isinstance(da, Dataset) and var is not None:
            self.mode = 'ds'
            self.da = da[var]
            self.ds = da
        else:
            raise TypeError('da must be an xarray DataArray or Dataset')
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.set_window_title(f'Explorer: {dim}-line')
        self.dim = dim
        self.autoscale = True
        self.orientation = orientation
        self.update_method = update_method

        self.log = False
        self.fig.subplots_adjust(bottom=0.2)
        self.ax_check_log = self.fig.add_axes([0.15, 0.05, 0.075, 0.075])
        self.check_log = CheckButtons(ax=self.ax_check_log, labels=['Log', 'Autoscale'], actives=[False, True])
        self.check_log.on_clicked(self.on_click_log)

        plot_orientation = {orientation: dim}
        if self.mode == 'da':
            self.plot = self.reduced_da().plot(ax=self.ax, **plot_orientation) #, **plot_kwargs
        elif self.mode == 'ds':
            self.ds = self.init_ds(self.ds, self.var)
            test = merge(self.format_ds()).to_array()
            self.plot = test.plot(ax=self.ax, hue='variable', **plot_orientation)  # , **plot_kwargs

    @staticmethod
    def init_ds(ds, var):
        """
        This function rearranges ds so that var is in the first position
        :param ds: xarray.Dataset
        :param var: Hashable name of the data_variable
        :return: Rearranged Dataset
        """
        data_vars = list(ds.data_vars.keys())
        if var not in data_vars:
            raise ValueError('var argument was not found in data_vars')
        data_vars.remove(var)
        data_vars.insert(0, var)
        ds = merge([ds[key] for key in data_vars])
        return ds

    def update_plot(self):
        if self.mode == 'da':
            data = self.reduced_da()
            x_data = data[self.dim].data
            y_data = data.data
            self.ax.autoscale_view()
            if self.log:
                minim = data.where(data>0).min()
            else:
                minim = data.min()
            if self.orientation == 'x':
                self.plot[0].set_data(x_data, y_data)
                if self.autoscale:
                    self.ax.set_ylim(minim, data.max())
            elif self.orientation == 'y':
                self.plot[0].set_data(y_data, x_data)
                if self.autoscale:
                    self.ax.set_xlim(minim, data.max())
        elif self.mode == 'ds':
            datas = self.format_ds()
            minim = []
            maxim = []
            for i, data in enumerate(datas):
                x_data = data[self.dim].data
                y_data = data.data
                if self.log:
                    minim.append(data.where(data > 0).min())
                else:
                    minim.append(data.min())
                maxim.append(data.max())
                if self.orientation == 'x':
                    self.plot[i].set_data(x_data, y_data)
                elif self.orientation == 'y':
                    self.plot[i].set_data(y_data, x_data)
            minim = min(minim)
            maxim = max(maxim)
            if self.autoscale:
                if self.orientation == 'y':
                    self.ax.set_xlim(minim, maxim)
                if self.orientation == 'x':
                    self.ax.set_ylim(minim, maxim)
        self.fig.canvas.draw()

    def on_click_log(self, label):
        f = {'x': self.ax.set_yscale, 'y': self.ax.set_xscale}[self.orientation]
        if label == 'Log':
            if not self.log:
                self.log = True
                f('log')
            elif self.log:
                self.log = False
                f('linear')
        elif label == 'Autoscale':
            if self.autoscale:
                self.autoscale = False
            else:
                self.autoscale = True

        self.update_plot()

    def reduced_da(self):
        red_slice = self.update_method().copy()
        del (red_slice[self.dim])
        da = self.da
        for x in red_slice.keys():
            if x in self.da.coords.keys():
                da = da.sel({x: red_slice[x]})
            else:
                da = da.isel({x: red_slice[x]})
        da = da.mean(list(red_slice.keys()))
        return da

    def format_ds(self):
        red_slice = self.update_method().copy()
        del (red_slice[self.dim])

        ds = self.ds
        for x in red_slice.keys():
            if x in self.da.coords.keys():
                ds = ds.sel({x: red_slice[x]})
            else:
                ds = ds.isel({x: red_slice[x]})
        ds = ds.mean(list(red_slice.keys()))

        test = broadcast(*[ds[var] for var in ds.data_vars.keys()])
        return list(test)


class SlicePlot:
    def __init__(self, da, ax, x_dim, y_dim, update_method, var=None, fig=None, plot_kwargs=None):
        fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        if plot_kwargs is None:
            plot_kwargs = {}
        self.ax = ax
        self.var = var
        if isinstance(da, DataArray):
            self.mode = 'da'
            self.da = da
        elif isinstance(da, Dataset):
            self.mode = 'ds'
            self.da = da[var]
            self.ds = da
        else:
            raise TypeError('da must be an xarray DataArray or Dataset')
        self.fig = fig
        self.fig.canvas.manager.set_window_title(f'Explorer: {y_dim} vs. {x_dim}')
        self.fig.subplots_adjust(bottom=0.28)
        self.update_method = update_method
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.plot = self.reduced_da().plot(x=x_dim, y=y_dim, **plot_kwargs)

        self.ax_xline = self.fig.add_axes([0.15, 0.05, 0.075, 0.075])
        self.b_xline = Button(self.ax_xline, f'x line')
        self.b_xline.on_clicked(self.on_click_xline)
        self.spx = None

        self.ax_yline = self.fig.add_axes([0.25, 0.05, 0.075, 0.075])
        self.b_yline = Button(self.ax_yline, f'y line')
        self.b_yline.on_clicked(self.on_click_yline)
        self.spy = None

        self.log_color = False
        self.ax_check_log_color = self.fig.add_axes([0.35, 0.05, 0.15, 0.075])
        self.check_log = CheckButtons(ax=self.ax_check_log_color, labels=['Log Color', 'Autoscale'], actives=[False, True])
        self.check_log.on_clicked(self.on_click_log_color)
        self.autoscale = True

        self.ax_lowerlimits = self.fig.add_axes([0.55, 0.05, 0.125, 0.075])
        self.text_lower = TextBox(self.ax_lowerlimits, '', initial='label')
        self.text_lower.on_submit(self.update_color_limits)
        self.ax_upperlimits = self.fig.add_axes([0.7, 0.05, 0.125, 0.075])
        self.text_upper = TextBox(self.ax_upperlimits, '', initial='label')
        self.text_upper.on_submit(self.update_color_limits)

        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)


        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                    useblit=True,
                                    button=[1, 3],  # don't use middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True,
                                    props=dict(facecolor='red', edgecolor='black', alpha=0.05, fill=True))
        self.grid_lock = False
        self.set_rectangle(self.update_method())

    def reduced_da(self):
        red_slice = self.update_method().copy()
        for i in [self.x_dim, self.y_dim]:
            del(red_slice[i])
        da = self.da
        for x in red_slice.keys():
            if x in self.da.coords.keys():
                da = da.sel({x: red_slice[x]})
            else:
                da = da.isel({x: red_slice[x]})
        da = da.mean(list(red_slice.keys()))
        return da

    def on_click_xline(self, event):
        if self.mode == 'ds':
            data = self.ds
        elif self.mode == 'da':
            data = self.da
        else:
            raise AttributeError('SlicePlot.mode must be "da" or "ds"')
        self.spx = SlicePlot1D(data, self.x_dim, self.update_method, 'x', var=self.var)
        self.spx.ax.sharex(self.ax)
        plt.show()

    def on_click_yline(self, event):
        if self.mode == 'ds':
            data = self.ds
        elif self.mode == 'da':
            data = self.da
        else:
            raise AttributeError('SlicePlot.mode must be "da" or "ds"')
        self.spy = SlicePlot1D(data, self.y_dim, self.update_method, 'y', var=self.var)
        self.spy.ax.sharey(self.ax)
        plt.show()

    def on_click_log_color(self, label):
        if label == 'Log Color':
            if self.log_color:
                self.log_color = False
                norm = Normalize()
                self.plot.set_norm(norm)
            elif ~self.log_color:
                self.log_color = True
                norm = LogNorm()
                self.plot.set_norm(norm)
        elif label == 'Autoscale':
            if self.autoscale:
                self.autoscale = False
            else:
                self.autoscale = True
        self.update_plot()

    def update_plot(self):
        data = self.reduced_da().transpose(self.y_dim, self.x_dim).data
        self.plot.set_array(data)
        if self.autoscale:
            self.plot.autoscale()
        lower, upper = self.plot.get_clim()
        self.text_lower.set_val(f'{lower:.2e}')
        self.text_upper.set_val(f'{upper:.2e}')
        self.fig.canvas.draw()
        if self.spx is not None:
            self.spx.update_plot()
        if self.spy is not None:
            self.spy.update_plot()

    def update_color_limits(self, event):
        try:
            upper, lower = float(self.text_upper.text), float(self.text_lower.text)
            self.plot.set_clim(lower, upper)
            self.update_plot()
        except ValueError:
            print('The entered value was not a valid float')


    def on_scroll(self, event):
        pass

    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        sl = self.update_method({self.x_dim: slice(x1, x2), self.y_dim: slice(y1, y2)})

    def set_rectangle(self, sl):
        old_extents = self.RS.extents
        x, y = sl[self.x_dim], sl[self.y_dim]
        extents_request = [x.start, x.stop, y.start, y.stop]
        extents = []
        for i, j in zip(extents_request, old_extents):
            if i is not None:
                extents.append(i)
            else:
                extents.append(j)
        self.RS.extents = tuple(extents)
        self.update_plot()

    def on_key_press(self, event):
        key = event.key
        if key in ['ctrl+up', 'ctrl+down', 'ctrl+left', 'ctrl+right']:
            # sl = self.update_method(None)
            ex = self.RS.extents
            dx = (ex[1]-ex[0])/2
            dy = (ex[3] - ex[2])/2
            if key == 'ctrl+right':
                self.RS.extents = ex[0]+dx, ex[1]+dx, ex[2], ex[3]
            elif key == 'ctrl+left':
                self.RS.extents = ex[0]-dx, ex[1]-dx, ex[2], ex[3]
            elif key == 'ctrl+up':
                self.RS.extents = ex[0], ex[1], ex[2]+dy, ex[3]+dy
            elif key == 'ctrl+down':
                self.RS.extents = ex[0], ex[1], ex[2]-dy, ex[3]-dy
            ex = self.RS.extents
            sl = self.update_method({self.x_dim: slice(ex[0], ex[1]), self.y_dim: slice(ex[2], ex[3])})



class Explorer:
    def __init__(self, da, cuts='minimal', var=None, save_path = 'ROI.sl', plot_kwargs=None, dimensions=None):
        self.save_path = save_path
        if plot_kwargs is None:
            plot_kwargs = {}
        if isinstance(da, DataArray):
            self.mode = 'da'
            self.da = da
        elif isinstance(da, Dataset):
            self.mode = 'ds'
            self.da = da[var]
            self.ds = da
        else:
            raise TypeError('da must be an xarray DataArray or Dataset')
        self.plot_axes = list(combinations(self.da.dims, 2))


        if cuts == 'minimal':
            self.plot_axes = self.plot_axes[:len(self.da.shape)-1]
        elif cuts == 'full':
            pass
        else:
            raise ValueError('cuts must be "minimal" or "full"')
        self.hyper_slice = {}
        for x in da.dims:
            if x in da.coords.keys():
                r = da.coords[x]
                self.hyper_slice[x] = slice(r.min(), r.max())
            else:
                self.hyper_slice[x] = slice(None, None)

        self.record = {}
        self.control_window = ControlWindow(self.record)
        self.control_window.close_all = self.close_all
        self.control_window.capture = self.capture
        self.control_window.save = self.save
        self.control_window.load = self.load
        self.control_window.select = self.select

        self.axes = []
        for (y_dim, x_dim) in self.plot_axes:
            fig, ax = plt.subplots()
            print(y_dim, x_dim)
            for q in self.axes:
                print(self.axes)
                if q.y_dim == y_dim:
                    try:
                        q.ax.sharey(ax)
                    except ValueError:
                        pass
                if q.x_dim == x_dim:
                    try:
                        q.ax.sharex(ax)
                    except ValueError:
                        pass
                print('yep')
            self.axes.append(SlicePlot(da, ax, x_dim, y_dim, self.update, var=var, fig=fig, plot_kwargs=plot_kwargs))

    def close_all(self, event):
        for x in self.axes:
            plt.close(x.fig)

    def update(self, sl=None):
        """
        Function that triggers the updates of the selection.
        :return: Dictionary of slices
        """
        if sl is not None:
            for i, j in sl.items():
                self.hyper_slice[i] = j
            for x in self.axes:
                x.set_rectangle(self.hyper_slice)
        return self.hyper_slice

    def update_plots(self):
        for x in self.axes:
            x.update_plot()
        for x in self.axes:
            x.set_rectangle(self.hyper_slice)

    def capture(self, label):
        self.record[label] = self.hyper_slice.copy()
        print(self.record)
        return self.record.keys()

    def save(self):
        with open(self.save_path, 'wb') as f:
            dump(self.record, f)

    def load(self):
        with open(self.save_path, 'rb') as f:
            self.record = load(f)
        key = list(self.record.keys())[0]
        self.hyper_slice = self.record[key]
        self.control_window._select(key)
        self.update_plots()
        return list(self.record.keys())

    def select(self, label):
        self.hyper_slice = self.record[label]
        print(label)
        self.update_plots()


class ControlWindow:
    def __init__(self, record):
        self.record = record
        self.fig = plt.figure(figsize=(3, 3))
        self.capture = self.not_set
        self.save = self.not_set
        self.load = self.not_set
        self.close_all = self.not_set
        self.select = self.not_set

        self.buttons = {'Capture': self._capture, 'Save': self._save, 'Load': self._load, 'Close all': self._close_all}
        self.axes = self.buttons.copy()

        self.grid = self.fig.add_gridspec(len(self.buttons)+1, 2)
        for i, label in enumerate(self.buttons.keys()):
            f = self.buttons[label]
            self.axes[label] = self.fig.add_subplot(self.grid[i, 0])
            self.buttons[label] = Button(self.axes[label], label=label)
            self.buttons[label].on_clicked(f)
        self.axes['label'] = self.fig.add_subplot(self.grid[-1, 0])
        self.caption = TextBox(self.axes['label'], '', initial='label')
        self.axes['selector'] = None
        self.selector = None
        # self.selector.on_clicked(self._select)

    def not_set(self, *args, **kwargs):
        print('This function has not been set.')

    def _capture(self, event):
        keys = self.capture(self.caption.text)
        self._update_selector(keys)
        self.fig.canvas.draw()

    def _update_selector(self, keys):
        if self.axes['selector'] is None:
            self.axes['selector'] = self.fig.add_subplot(self.grid[0:, 1])
        else:
            self.axes['selector'].clear()
        self.selector = RadioButtons(self.axes['selector'], list(keys), active=len(keys)-1)
        self.selector.on_clicked(self._select)

    def _save(self, event):
        self.save()

    def _load(self, event):
        keys = self.load()
        self._update_selector(keys)

    def _select(self, event):
        self.select(event)

    def _close_all(self, event):
        self.close_all(event)
        plt.close(self.fig)
