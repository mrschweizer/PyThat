from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from matplotlib.widgets import Button

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
        plot_orientation = {orientation: dim}
        self.plot = self.reduced_da().plot(ax=self.ax, **plot_orientation) #, **plot_kwargs

    def update_plot(self):
        data = self.reduced_da()
        x_data = data[self.dim].data
        y_data = data.data
        self.ax.autoscale_view()
        if self.orientation == 'x':
            self.plot[0].set_data(x_data, y_data)
            if self.autoscale:
                self.ax.set_ylim(data.min(),data.max())
        elif self.orientation == 'y':
            self.plot[0].set_data(y_data, x_data)
            if self.autoscale:
                self.ax.set_xlim(data.min(), data.max())
        self.fig.canvas.draw()

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
        # fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
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


        # self.da.plot.pcolormesh(x=x_dim, y=y_dim, ax=ax, **plot_kwargs)
        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                    useblit=True,
                                    button=[1, 3],  # don't use middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)
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
        # print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        # print(" The button you used were: %s %s" % (eclick.button, erelease.button))

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

        print(self.plot_axes)
        self.axes = []
        for (y_dim, x_dim) in self.plot_axes:
            fig, ax = plt.subplots()
            for q in self.axes:
                if q.y_dim == y_dim:
                    ax.sharey(q.ax)
                if q.x_dim == x_dim:
                    ax.sharex(q.ax)
            self.axes.append(SlicePlot(da, ax, x_dim, y_dim, self.update, fig=fig, plot_kwargs=plot_kwargs))

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
