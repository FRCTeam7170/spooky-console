
"""
TODO
"""

import tkinter as tk
import tkinter.font as tkfont
import typing
import os
from collections import deque
from PIL import Image, ImageTk
import spookyconsole.gui.style as style
with style.patch():
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.style as mplstyle
import matplotlib.figure as mplfigure
import matplotlib.animation as mplani
import matplotlib as mpl
from spookyconsole.gui.core import DockableMixin
from spookyconsole import DATA_PATH


MPL_STYLE = {}


def _tk_font_family_to_mpl_font_family(tk_family):
    if tk_family in ("Courier", "Courier New"):
        return "monospace"
    elif tk_family in ("Arial", "Helvetica"):
        return "sans-serif"
    elif tk_family in ("Times", "Times New Roman"):
        return "serif"
    return None


def init_mpl_rcparams(style):
    font = style.get_style("font")
    if isinstance(font, str):
        try:
            font = tkfont.nametofont(font)
        except tk.TclError:
            font = tkfont.Font(font=font)
    elif isinstance(font, tuple):
        font = tkfont.Font(font=font)
    actual_font = font.actual()
    font_family = _tk_font_family_to_mpl_font_family(actual_font["family"])
    if font_family:
        MPL_STYLE["font.family"] = font_family
    MPL_STYLE["font.style"] = "normal" if actual_font["slant"] == tkfont.ROMAN else "italic"
    MPL_STYLE["font.weight"] = actual_font["weight"]
    MPL_STYLE["font.size"] = actual_font["size"]

    bg = style.get_style("bg") or style.get_style("background")
    if bg:
        MPL_STYLE["axes.facecolor"] = bg
        MPL_STYLE["figure.facecolor"] = bg

    fg = style.get_style("fg") or style.get_style("foreground")
    if fg:
        MPL_STYLE["grid.color"] = fg
        MPL_STYLE["xtick.color"] = fg
        MPL_STYLE["ytick.color"] = fg

    bd = style.get_style("highlightcolor")
    if bd:
        MPL_STYLE["axes.edgecolor"] = bd
        MPL_STYLE["figure.edgecolor"] = bd


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


class PlotToolbar(style.Frame):

    def __init__(self, master, plot, *args, checkbutton_style=None, **kwargs):
        def_style = kwargs.get("style")
        super().__init__(master, *args, **kwargs)

        self.plot = plot
        self.relim_var = tk.BooleanVar(self)
        self.update_var = tk.BooleanVar(self)
        self.relim_checkbutton = style.Checkbutton(self, style=(checkbutton_style or def_style),
                                                   text="Relim", var=self.relim_var)
        self.update_checkbutton = style.Checkbutton(self, style=(checkbutton_style or def_style),
                                                    text="Update", var=self.update_var)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
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


class CustomTkNavBar(NavigationToolbar2Tk):

    def __init__(self, *args, button_style=None, **kwargs):
        self.button_style = button_style
        super().__init__(*args, **kwargs)

    def _Button(self, text, file, command, extension='.png'):
        path = os.path.join(DATA_PATH, "images", file + extension)
        image = ImageTk.PhotoImage(Image.open(path))
        b = style.Button(self, style=self.button_style, text=text, command=command, padx=2, pady=2, image=image)
        b._ntimage = image
        b.pack(side=tk.LEFT)
        return b


class Plot(style.Frame):

    FRAME_PAD = 2

    def __init__(self, master, nrows=1, ncols=1, figure_mplstyle="ggplot", figure_style=None,
                 button_style=None, checkbutton_style=None, *args, **kwargs):
        def_style = kwargs.get("style")
        super().__init__(master, *args, **kwargs)

        with mplstyle.context(figure_mplstyle):
            mpl.rcParams.update(MPL_STYLE)
            self.figure = mplfigure.Figure((0.1, 0.1))
            self.frame = style.Frame(self, style=def_style, padx=self.FRAME_PAD, pady=self.FRAME_PAD)
            with style.patch():
                with style.stylize(figure_style or def_style):
                    self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
                    self.nav_bar = CustomTkNavBar(self.canvas, self.frame, button_style=button_style)
            self.extra_bar = PlotToolbar(self.frame, self, checkbutton_style=checkbutton_style, style=def_style)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.extra_bar.pack(fill=tk.X)
            self.frame.pack(fill=tk.BOTH, expand=True)

            if nrows and ncols:
                self.figure.subplots(nrows, ncols)


class DockablePlot(DockableMixin, Plot):

    def __init__(self, master, row_span=9, col_span=9, *args, **kwargs):
        super().__init__(master, row_span, col_span, *args, **kwargs)
        self.bind_drag_on(self.extra_bar)
