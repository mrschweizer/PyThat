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

class SlicePlot1D:
    def __init__(self, da, dim, update_method, orientation, plot_kwargs=None):
        if plot_kwargs is not None:
            self.plot_kwargs = plot_kwargs.copy()
        else:
            self.plot_kwargs = {}
        print(self.plot_kwargs)
        self.da = da
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.set_window_title(f'Explorer: {dim}-line')
        self.dim = dim
        self.autoscale = True
        self.orientation = orientation
        self.update_method = update_method

        self.log = False
        self.fig.subplots_adjust(bottom=0.2)
        self.ax_check_log = self.fig.add_axes([0.15, 0.05, 0.075, 0.075])
        self.check_log = CheckButtons(ax=self.ax_check_log, labels=['Log'])
        self.check_log.on_clicked(self.on_click_log)

        plot_orientation = {orientation: dim}
        self.plot = self.reduced_da().plot(ax=self.ax, **plot_orientation) #, **plot_kwargs

    def update_plot(self):
        data = self.reduced_da()
        x_data = data[self.dim].data
        y_data = data.data
        self.ax.autoscale_view()
        if self.log:
            min = data.where(data>0).min()
        else:
            min = data.min()
        if self.orientation == 'x':
            self.plot[0].set_data(x_data, y_data)
            if self.autoscale:
                self.ax.set_ylim(min, data.max())
        elif self.orientation == 'y':
            self.plot[0].set_data(y_data, x_data)
            if self.autoscale:
                self.ax.set_xlim(min, data.max())
        self.fig.canvas.draw()

    def on_click_log(self, label):
        f = {'x': self.ax.set_yscale, 'y': self.ax.set_xscale}[self.orientation]

        if not self.log:
            self.log = True
            f('log')
        elif self.log:
            print('linear')
            self.log = False
            f('linear')

        self.update_plot()


    def reduced_da(self):
        # TODO: Offer multiple reduce methods
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

class SlicePlot:
    def __init__(self, da, ax, x_dim, y_dim, update_method, fig=None, plot_kwargs=None):
        fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        if plot_kwargs is None:
            plot_kwargs = {}
        self.ax = ax
        self.da = da
        self.fig = fig
        # print(dir(self.fig.canvas.manager))
        self.fig.canvas.manager.set_window_title(f'Explorer: {y_dim} vs. {x_dim}')
        self.fig.subplots_adjust(bottom=0.2)
        self.update_method = update_method
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.plot = self.reduced_da().plot(x=x_dim, y=y_dim, **plot_kwargs)

        self.ax_xline = self.fig.add_axes([0.15, 0.05, 0.075, 0.075])
        self.b_xline = Button(self.ax_xline, f'{self.x_dim} line')
        self.b_xline.on_clicked(self.on_click_xline)
        self.spx = None

        self.ax_yline = self.fig.add_axes([0.25, 0.05, 0.075, 0.075])
        self.b_yline = Button(self.ax_yline, f'{self.y_dim} line')
        self.b_yline.on_clicked(self.on_click_yline)
        self.spy = None

        self.log_color = False
        self.ax_check_log_color = self.fig.add_axes([0.4, 0.05, 0.075, 0.075])
        self.check_log = CheckButtons(ax=self.ax_check_log_color, labels=['Log Color'])
        self.check_log.on_clicked(self.on_click_log_color)


        # self.da.plot.pcolormesh(x=x_dim, y=y_dim, ax=ax, **plot_kwargs)
        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                    useblit=True,
                                    button=[1, 3],  # don't use middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True,
                                    props=dict(facecolor='red', edgecolor='black', alpha=0.05, fill=True))
        self.set_rectangle(self.update_method())

    def reduced_da(self):
        # TODO: Offer multiple reduce methods
        red_slice = self.update_method().copy()
        for i in [self.x_dim, self.y_dim]:
            del(red_slice[i])
        # print(f'reduced slice: {red_slice}')
        da = self.da
        for x in red_slice.keys():
            if x in self.da.coords.keys():
                da = da.sel({x: red_slice[x]})
            else:
                da = da.isel({x: red_slice[x]})
        da = da.mean(list(red_slice.keys()))
        return da

    def on_click_xline(self, event):
        self.spx = SlicePlot1D(self.da, self.x_dim, self.update_method, 'x')
        self.spx.ax.sharex(self.ax)
        plt.show()

    def on_click_yline(self, event):
        self.spy = SlicePlot1D(self.da, self.y_dim, self.update_method, 'y')
        self.spy.ax.sharey(self.ax)
        plt.show()

    def on_click_log_color(self, label):
        if self.log_color:
            self.log_color = False
            norm = Normalize()
            self.plot.set_norm(norm)
        elif ~self.log_color:
            self.log_color = True
            norm = LogNorm()
            self.plot.set_norm(norm)
        self.update_plot()
        print(self.log_color)

    def update_plot(self):
        data = self.reduced_da().transpose(self.y_dim, self.x_dim).data
        self.plot.set_array(data)
        self.plot.autoscale()
        self.fig.canvas.draw()
        if self.spx is not None:
            self.spx.update_plot()
        if self.spy is not None:
            self.spy.update_plot()

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
        print(key)
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
    def __init__(self, da, cuts='minimal', plot_kwargs=None):
        if plot_kwargs is None:
            plot_kwargs = {}
        self.da = da
        self.plot_axes = list(combinations(da.dims, 2))
        if cuts == 'minimal':
            self.plot_axes = self.plot_axes[:len(da.shape)-1]
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
            self.axes.append(SlicePlot(da, ax, x_dim, y_dim, self.update, fig=fig, plot_kwargs=plot_kwargs))

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
        with open('ROI.sl', 'wb') as f:
            dump(self.record, f)

    def load(self):
        with open('ROI.sl', 'rb') as f:
            self.record = load(f)
        print(self.record)

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
        if self.axes['selector'] is None:
            self.axes['selector'] = self.fig.add_subplot(self.grid[0:, 1])
        else:
            self.axes['selector'].clear()
        self.selector = RadioButtons(self.axes['selector'], list(keys))
        self.selector.on_clicked(self._select)
        self.fig.canvas.draw()


    def _save(self, event):
        self.save()

    def _load(self, event):
        self.load()

    def _select(self, event):
        self.select(event)

    def _close_all(self, event):
        self.close_all(event)
        plt.close(self.fig)
