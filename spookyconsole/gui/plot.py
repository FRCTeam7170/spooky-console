
"""
TODO
"""

from collections import deque
import typing
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.style as mplstyle
from matplotlib.figure import Figure
import matplotlib.animation as mplani
from .core import DockableMixin


class LiveUpdater:

    def __init__(self, line, plot, interval=1000, feeder=None, max_data_cardinality=None):
        self.line = line
        self.plot = plot
        self.feeder = feeder
        self.max_data_cardinality = max_data_cardinality
        self._x_data = deque(maxlen=max_data_cardinality)
        self._x_data.extend(line.get_xdata())
        self._y_data = deque(maxlen=max_data_cardinality)
        self._y_data.extend(line.get_ydata())
        line.set_data(self._x_data, self._y_data)
        if interval:
            self.ani = mplani.FuncAnimation(self.axes.get_figure(), self.update, interval=interval)
            plot.canvas.draw()

    @property
    def axes(self):
        return self.line.axes

    def feed(self, x, y):
        if not isinstance(x, typing.Iterable):
            x = [x]
        if not isinstance(y, typing.Iterable):
            y = [y]
        self._x_data.extend(x)
        self._y_data.extend(y)

    def update(self, _=None):
        if self.plot.extra_bar.autoupdate:
            if self.feeder:
                self.feed(*self.feeder())
            self.line.recache_always()
            if self.plot.extra_bar.relim:
                if self.axes.get_autoscale_on():
                    self._refit_artists()
                else:
                    self.plot.extra_bar.relim = False

    def _refit_artists(self):
        self.axes.relim()
        self.axes.autoscale_view()


class PlotToolbar(tk.Frame):

    def __init__(self, master, plot, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.plot = plot
        self.relim_var = tk.BooleanVar(self)
        self.update_var = tk.BooleanVar(self)
        self.relim_checkbutton = tk.Checkbutton(self, text="Relim", var=self.relim_var)
        self.update_checkbutton = tk.Checkbutton(self, text="Update", var=self.update_var)

        self.relim_checkbutton.grid(row=0, column=0)
        self.update_checkbutton.grid(row=0, column=1)
        self.relim_var.set(True)
        self.update_var.set(True)
        self.relim_var.trace_add("write", self._relim_trace_callback)

    @property
    def relim(self):
        return self.relim_var.get()

    @relim.setter
    def relim(self, val):
        self.relim_var.set(val)

    @property
    def autoupdate(self):
        return self.update_var.get()

    @autoupdate.setter
    def autoupdate(self, val):
        self.update_var.set(val)

    def _relim_trace_callback(self, *_):
        if self.relim_var.get():
            for axis in self.plot.figure.get_axes():
                axis.set_autoscale_on(True)


class Plot(tk.Frame):
    """
    TODO: some of the "get" calls might have a significant overhead in extreme cases; it may be worth employing a
        cache system if performance is an issue.
    """

    FRAME_PAD = 2

    def __init__(self, master, nrows=1, ncols=1, style="ggplot", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.figure = Figure((0.1, 0.1))
        self.frame = tk.Frame(self, padx=self.FRAME_PAD, pady=self.FRAME_PAD)
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.nav_bar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.extra_bar = PlotToolbar(self.frame, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.extra_bar.pack()
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.style = style
        if nrows and ncols:
            with mplstyle.context(style):
                self.figure.subplots(nrows, ncols)


class DockablePlot(DockableMixin, Plot):

    def __init__(self, master, row_span=9, col_span=9, *args, **kwargs):
        super().__init__(master, row_span, col_span, *args, **kwargs)
        self.bind_drag_on(self.extra_bar)
