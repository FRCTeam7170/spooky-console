
"""Contains Matplotlib plotting support for tkinter GUIs."""

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
from spookyconsole import RESOURCE_PATH


mpl_style = {}
"""A dictionary of matplotlib styles to override the matplotlib stylesheet styles in ``Plot``."""


def _tk_font_family_to_mpl_font_family(tk_family):
    """
    Convert the given tkinter font family to a roughly equivalent matplotlib font family. Currently only the cross-
    platform tkinter font families are supported.

    :param tk_family: The tkinter font family to convert.
    :type tk_family: str
    :return: The equivalent matplotlib font family.
    :rtype: str
    """
    if tk_family in ("Courier", "Courier New"):
        return "monospace"
    elif tk_family in ("Arial", "Helvetica"):
        return "sans-serif"
    elif tk_family in ("Times", "Times New Roman"):
        return "serif"
    return None


def init_mpl_rcparams(style):
    """
    Initialize ``mpl_style`` with equivalent tkinter styles from the given ``Style`` object.

    :param style: The ``Style`` object to initialize ``mpl_style`` from.
    :type style: spookyconsole.gui.style.Style
    """
    font = style.get_style("font")
    if isinstance(font, str):
        try:
            # Maybe the font is a named font...
            font = tkfont.nametofont(font)
        except tk.TclError:
            # Otherwise it must be in the form: "family size style"
            font = tkfont.Font(font=font)
    # If the font is in this form: (family, size, style)
    elif isinstance(font, tuple):
        font = tkfont.Font(font=font)
    actual_font = font.actual()
    font_family = _tk_font_family_to_mpl_font_family(actual_font["family"])
    if font_family:
        mpl_style["font.family"] = font_family
    mpl_style["font.style"] = "normal" if actual_font["slant"] == tkfont.ROMAN else "italic"
    # No conversion required here; both mpl and tk accept "normal" and "bold" as font weights.
    mpl_style["font.weight"] = actual_font["weight"]
    mpl_style["font.size"] = actual_font["size"]

    bg = style.get_style("bg") or style.get_style("background")
    if bg:
        mpl_style["axes.facecolor"] = bg
        mpl_style["figure.facecolor"] = bg

    fg = style.get_style("fg") or style.get_style("foreground")
    if fg:
        mpl_style["grid.color"] = fg
        mpl_style["xtick.color"] = fg
        mpl_style["ytick.color"] = fg

    bd = style.get_style("highlightcolor")
    if bd:
        mpl_style["axes.edgecolor"] = bd
        mpl_style["figure.edgecolor"] = bd


class LiveUpdater:
    """
    TODO
    """

    def __init__(self, line, plot, interval=1000, feeder=None, max_data_cardinality=None):
        """
        :param line: The matplotlib line that this ``LiveUpdater`` is responsible for updating.
        :type line: matplotlib.lines.Line2D
        :param plot: The ``Plot`` object that contains the given ``line``.
        :type plot: Plot
        :param interval: How long in milliseconds to wait in between updates.
        :type interval: int
        :param feeder: A callable that returns an ``(x, y)`` 2-tuple of data. ``x`` and ``y`` may be single data points
        or containers of many values. This is called every update... TODO
        :param max_data_cardinality: Maximum number of data points to store at once.
        :type max_data_cardinality: int
        """
        self.line = line
        """The ``matplotlib.lines.Line2D`` that this ``LiveUpdater`` is responsible for updating."""

        self.plot = plot
        """The ``Plot`` object that contains ``LiveUpdater.line``."""

        self.feeder = feeder
        """"""

        self._x_data = deque(maxlen=max_data_cardinality)
        """"""

        self._y_data = deque(maxlen=max_data_cardinality)
        """"""

        self._x_data.extend(line.get_xdata())
        self._y_data.extend(line.get_ydata())
        # Setting a Line2D's data explicitly like this causes it to store a reference (not a copy!) to the objects
        # passed in, which is useful in this case because deques are mutable so we needn't ever call set_data again--we
        # need only append to the deques and then signal for the line to recache.
        line.set_data(self._x_data, self._y_data)
        if interval:
            self.ani = mplani.FuncAnimation(self.axes.get_figure(), self.update, interval=interval)
            """
            The ``matplotlib.animation.FuncAnimation`` used for this ``LiveUpdater``. A reference to this object is only
            kept out of necessity.
            """
            # We explicitly redraw the canvas because matplotlib Animations are triggered on draw events and, if it is
            # already drawn, the canvas may never get drawn again.
            plot.canvas.draw()

    @property
    def axes(self):
        """
        :return: The axes containing this ``LiveUpdater``'s ``LiveUpdater.line``.
        :rtype: matplotlib.axes.Axes
        """
        return self.line.axes

    def feed(self, x, y):
        """
        Append the given ``x`` and ``y`` data to this ``LiveUpdater``'s ``LiveUpdater.line``'s data.

        :param x: The x data to append. May be a single value or some container of multiple values.
        :param y: The y data to append. May be a single value or some container of multiple values.
        """
        if not isinstance(x, typing.Iterable):
            x = [x]
        if not isinstance(y, typing.Iterable):
            y = [y]
        self._x_data.extend(x)
        self._y_data.extend(y)

    def update(self, _=None):
        """
        Update this ``LiveUpdater``'s ``LiveUpdater.line``. TODO: WORKING HERE
        """
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
        """Refit the artists contained on ``LiveUpdater.axes`` (namely ``LiveUpdater.line``) into view."""
        # TODO: use the same logic here to coalesce multiple calls as in gui.core.Grid for periodic resizing?
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
        path = os.path.join(RESOURCE_PATH, "images", file + extension)
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
            mpl.rcParams.update(mpl_style)
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
    """Dockable version of ``Plot``."""

    def __init__(self, master, col_span=9, row_span=9, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param col_span: The column span (width) of this widget on the grid.
        :type col_span: int
        :param row_span: The row span (height) of this widget on the grid.
        :type row_span: int
        :param args: Additional args for the ``Plot`` constructor.
        :param kwargs: Additional kwargs for the ``Plot`` constructor.
        """
        super().__init__(master, col_span, row_span, *args, **kwargs)
        self.bind_drag_on(self.extra_bar)
