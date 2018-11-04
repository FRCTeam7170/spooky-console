
"""Contains Matplotlib plotting support for tkinter GUIs."""

import tkinter as tk
import tkinter.font as tkfont
import typing
import os
from collections import deque
from PIL import Image, ImageTk
import spookyconsole.gui.style as style
with style.patch():
    # These imports are patched so that the subclasses of tkinter widgets actually use their styleable equivalents.
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
    Class to handle updating a single ``matplotlib.lines.Line2D``. ``LiveUpdater``s can either be updated manually by
    invoking ``LiveUpdater.update`` or specifying a non-zero ``interval`` upon construction.

    A ``feeder`` may be specified in the constructor to be called every update to "feed" the line new data.

    If memory consumption is a concern, ``max_data_cardinality`` can be specified in the constructor to limit how many
    data points the line can have at once. Once the maximum is reached, the oldest data is discarded as necessary.
    """

    def __init__(self, line, plot, interval=1000, feeder=None, max_data_cardinality=None):
        """
        :param line: The matplotlib line that this ``LiveUpdater`` is responsible for updating.
        :type line: matplotlib.lines.Line2D
        :param plot: The ``Plot`` object that contains the given ``line``.
        :type plot: Plot
        :param interval: How long in milliseconds to wait in between updates. If set to zero, the ``LiveUpdater`` won't
        update automatically.
        :type interval: int
        :param feeder: A callable returning an ``(x, y)`` 2-tuple of data, where ``x`` and ``y`` may be single data
        points or containers of many values. This is called every update to "feed" data to the line.
        :param max_data_cardinality: Maximum number of data points to store at once.
        :type max_data_cardinality: int
        """
        self.line = line
        """The ``matplotlib.lines.Line2D`` that this ``LiveUpdater`` is responsible for updating."""

        self.plot = plot
        """The ``Plot`` object that contains ``LiveUpdater.line``."""

        self.feeder = feeder
        """
        A callable returning an ``(x, y)`` 2-tuple of data, where ``x`` and ``y`` may be single data points or
        containers of many values. This is called every update to "feed" data to the line.
        """

        self._x_data = deque(maxlen=max_data_cardinality)
        """The ``LiveUpdater.line``'s x data."""

        self._y_data = deque(maxlen=max_data_cardinality)
        """The ``LiveUpdater.line``'s y data."""

        self._x_data.extend(line.get_xdata())
        self._y_data.extend(line.get_ydata())
        # Setting a Line2D's data explicitly like this causes it to store a reference (not a copy!) to the objects
        # passed in, which is useful in this case because deques are mutable so we needn't ever call set_data again--we
        # need only append to the deques and then signal for the line to recache.
        line.set_data(self._x_data, self._y_data)
        if interval:
            self._ani = mplani.FuncAnimation(self.axes.get_figure(), self.update, interval=interval)
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
        """Update the ``LiveUpdater.line`` and relimit the axes so the updated line fits into view."""
        if self.plot.extra_bar.autoupdate:
            if self.feeder:
                self.feed(*self.feeder())
            # Because the line holds a reference to the x and y data deques (which are mutable), we need only recache
            # the line.
            self.line.recache_always()
            if self.plot.extra_bar.relim:
                # Whenever the tools on the nav bar are used (pan, zoom, etc.) the autoscaling on the axes gets turned
                # off.
                if self.axes.get_autoscale_on():
                    self._refit_artists()
                # If the autoscaling is off, but the relim checkbox on the plot's "extra bar" is enabled, we're
                # essentially in an invalid state since it's impossible to relim the axes while the user is using a nav
                # bar tool. Thus, disable the extra bar's relim checkbox.
                else:
                    self.plot.extra_bar.relim = False

    def _refit_artists(self):
        """Refit the artists contained on ``LiveUpdater.axes`` (namely the ``LiveUpdater.line``) into view."""
        # TODO: use the same logic here to coalesce multiple calls as in gui.core.Grid for periodic resizing?
        self.axes.relim()
        self.axes.autoscale_view()


class PlotToolbar(style.Frame):
    """
    Custom toolbar widget for ``Plot``s. At the moment, this toolbar only contains two checkboxes labelled "Relim" and
    "Update" which are to control the functionality of ``LiveUpdater``s.
    """

    def __init__(self, master, plot, *args, checkbutton_style=None, **kwargs):
        """
        :param master: The master tkinter widget.
        :param plot: The ``Plot`` containing this toolbar.
        :type plot: Plot
        :param args: Additional args for the ``spookyconsole.gui.style.Frame`` constructor.
        :param checkbutton_style: The style for the checkbuttons. Defaults to the style given for the frame (in kwargs).
        :type checkbutton_style: spookyconsole.gui.style.Style
        :param kwargs: Additional kwargs for the ``spookyconsole.gui.style.Frame`` constructor.
        """
        checkbutton_style = checkbutton_style or kwargs.get("style")
        super().__init__(master, *args, **kwargs)

        self.plot = plot
        """The ``Plot`` containing this toolbar."""

        self.relim_var = tk.BooleanVar(self)
        self.update_var = tk.BooleanVar(self)
        self.relim_checkbutton = style.Checkbutton(self, style=checkbutton_style, text="Relim", var=self.relim_var)
        self.update_checkbutton = style.Checkbutton(self, style=checkbutton_style, text="Update", var=self.update_var)

        # Make both checkboxes equally resizeable.
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
        """
        :return: Whether or not the relim checkbox is checked.
        :rtype: bool
        """
        return self.relim_var.get()

    @relim.setter
    def relim(self, val):
        """
        :param val: New value for the relim checkbox.
        :type val: bool
        """
        self.relim_var.set(val)

    @property
    def autoupdate(self):
        """
        :return: Whether or not the autoupdate checkbox is checked.
        :rtype: bool
        """
        return self.update_var.get()

    @autoupdate.setter
    def autoupdate(self, val):
        """
        :param val: New value for the autoupdate checkbox.
        :type val: bool
        """
        self.update_var.set(val)

    def _relim_trace_callback(self, *_):
        """
        Internal method used as the callback for changes to ``PlotToolbar.relim_var``. If the relim var changes to True,
        re-enables autoscaling on all the axes in ``PlotToolbar.plot``.
        """
        if self.relim_var.get():
            for axis in self.plot.axes:
                axis.set_autoscale_on(True)


class CustomTkNavBar(NavigationToolbar2Tk):
    """Override of the default matplotlib tkinter navigation bar so that the buttons can be styled."""

    def __init__(self, *args, button_style=None, **kwargs):
        """
        :param args: Args for the ``matplotlib.backends.backend_tkagg.NavigationToolbar2Tk`` constructor.
        :param button_style: The style for the buttons.
        :type button_style: spookyconsole.gui.style.Style
        :param kwargs: Kwargs for the ``matplotlib.backends.backend_tkagg.NavigationToolbar2Tk`` constructor.
        """
        self.button_style = button_style
        super().__init__(*args, **kwargs)

    def _Button(self, text, file, command, extension='.png'):
        # Note that the png photos are used instead of the gif ones. These have a transparent background making the
        # buttons automatically change colour as the bg style in button_style is changed. I tried to make the fg dynamic
        # too by generating new images for buttons every time the fg changes, but that's a little tricky and admittedly
        # too much work for such a trivial piece of this project.
        path = os.path.join(RESOURCE_PATH, "images", file + extension)
        image = ImageTk.PhotoImage(Image.open(path))
        b = style.Button(self, style=self.button_style, text=text, command=command, padx=2, pady=2, image=image)
        b._ntimage = image
        b.pack(side=tk.LEFT)
        return b


class Plot(style.Frame):
    """
    A matplotlib plot abstraction as a tkinter widget. The widget is composed of a ``matplotlib.figure.Figure`` and two
    bars: a ``CustomTkNavBar`` (containing the standard matplotlib nav bar tools) and a ``PlotToolbar`` (which is
    custom).
    """

    FRAME_PAD = 2
    """Amount of padding in pixels to place around the entire plot (figure and toolbars)."""

    def __init__(self, master, nrows=1, ncols=1, figure_mplstyle="ggplot", figure_style=None,
                 button_style=None, checkbutton_style=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param nrows: How many rows of subplots to initialize the figure with.
        :type nrows: int
        :param ncols: How many columns of subplots to initialize the figure with.
        :type ncols: int
        :param figure_mplstyle: The matplotlib style to use. This will be partially overwritten with ``mpl_style``.
        :type figure_mplstyle: str
        :param figure_style: The style for the figure. Defaults to the style given for the frame (in kwargs).
        :type figure_style: spookyconsole.gui.style.Style
        :param button_style: The style for the nav bar buttons. Defaults to the style given for the frame (in kwargs).
        :type button_style: spookyconsole.gui.style.Style
        :param checkbutton_style: The style for the ``PlotToolbar`` checkbuttons. Defaults to the style given for the
        frame (in kwargs).
        :type checkbutton_style: spookyconsole.gui.style.Style
        :param args: Additional args for the ``spookyconsole.gui.style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``spookyconsole.gui.style.Frame`` constructor.
        """
        def_style = kwargs.get("style")
        super().__init__(master, *args, **kwargs)

        with mplstyle.context(figure_mplstyle):
            mpl.rcParams.update(mpl_style)
            self.figure = mplfigure.Figure((0.1, 0.1))
            self.frame = style.Frame(self, style=def_style, padx=self.FRAME_PAD, pady=self.FRAME_PAD)
            with style.patch(), style.stylize(figure_style or def_style):
                self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
                self.nav_bar = CustomTkNavBar(self.canvas, self.frame, button_style=button_style)
            self.extra_bar = PlotToolbar(self.frame, self, checkbutton_style=checkbutton_style, style=def_style)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.extra_bar.pack(fill=tk.X)
            self.frame.pack(fill=tk.BOTH, expand=True)

            if nrows and ncols:
                self.figure.subplots(nrows, ncols)

    @property
    def axes(self):
        """
        :return: A list of this plot's axes.
        :rtype: list
        """
        return self.figure.get_axes()


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
