
"""
Extra tkinter widgets for the GUI component of spooky-console. Namely, dockable versions of all the builtin tkinter
widgets are provided here along with more specific widgets.
"""

import tkinter as tk
import math
from collections import deque
from spookyconsole import utils
from spookyconsole.nt import ntutils
from spookyconsole.gui.core import DockableMixin
from spookyconsole.gui import style
from spookyconsole.gui import popup


class DockableButton(DockableMixin, style.Button):
    pass


class DockableCanvas(DockableMixin, style.Canvas):
    pass


class DockableCheckbutton(DockableMixin, style.Checkbutton):
    pass


class DockableEntry(DockableMixin, style.Entry):
    pass


class DockableFrame(DockableMixin, style.Frame):
    pass


class DockableLabel(DockableMixin, style.Label):
    pass


class DockableLabelFrame(DockableMixin, style.LabelFrame):
    pass


class DockableListbox(DockableMixin, style.Listbox):
    pass


class DockableRadiobutton(DockableMixin, style.Radiobutton):
    pass


class DockableScale(DockableMixin, style.Scale):
    pass


class DockableSpinbox(DockableMixin, style.Spinbox):
    pass


class DockableText(DockableMixin, style.Text):
    pass


class BooleanIndicator(style.Frame):
    """
    A rectangular widget for displaying a boolean value indicated by two different colours. The indicator may or may not
    have a label on it. Also, the indicator can optionally be "mutable", meaning it can be clicked by the user to toggle
    it.
    """

    def __init__(self, master, text="", mutable=True, on_colour="green", off_colour="red",
                 label_style=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param text: The text to display on the indicator.
        :type text: str
        :param mutable: Whether or not the indicator may be toggled via the gui.
        :type mutable: bool
        :param on_colour: The colour the indicator will take on when enabled.
        :type on_colour: str
        :param off_colour: The colour the indicator will take on when disabled.
        :type off_colour: str
        :param label_style: The style for the label. Defaults to the style given for the frame (in kwargs).
        :type label_style: Style
        :param args: Additional args for the ``style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``style.Frame`` constructor.
        """
        super().__init__(master, *args, **kwargs)
        self.on_colour = on_colour
        self.off_colour = off_colour

        # Make the label resizable.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Only create the label if text is given.
        self.label = None
        if text:
            self.label = style.Label(self, style=(label_style or kwargs.get("style")), text=text)
            self.label.grid()

        if mutable:
            # If the indicator is to be mutable, bind click events on the frame (and the label, if it was created).
            self.bind("<Button-1>", self._on_click)
            if self.label:
                self.label.bind("<Button-1>", self._on_click)

        self.var = tk.BooleanVar(master)
        self.var.trace_add("write", self._on_change)
        self.value = True

    @property
    def value(self):
        """
        :return: The value of the indicator.
        :rtype: bool
        """
        return self.var.get()

    @value.setter
    def value(self, val):
        """
        :param val: New value for the indicator.
        :type val: bool
        """
        self.var.set(val)

    def _on_change(self, *_):
        """
        Internal method used as the callback for write events on ``BooleanIndicator.var``if the indicator is mutable.
        """
        # Change the colour of the frame (and, if it exists, the label) according to the new state of the indicator.
        colour = self.on_colour if self.value else self.off_colour
        self.configure(bg=colour)
        if self.label:
            self.label.configure(bg=colour)

    def _on_click(self, _):
        """
        Internal method used as the callback for "<Button-1>" events if the indicator is mutable. This method toggles
        the indicator's state.
        """
        self.value = not self.value


class DockableBooleanIndicator(DockableMixin, BooleanIndicator):
    """Dockable version of ``BooleanIndicator``."""

    def __init__(self, master, width=1, height=1, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param width: The width (column span) of this widget on the grid.
        :type width: int
        :param height: The height (row span) of this widget on the grid.
        :type height: int
        :param args: Additional args for the ``BooleanIndicator`` constructor.
        :param kwargs: Additional kwargs for the ``BooleanIndicator`` constructor.
        """
        super().__init__(master, width, height, *args, **kwargs)
        # If a label was given for the indicator, assure that it relays bind events to the DockableMixin.
        if self.label:
            self.bind_drag_on(self.label)


class LabelledText(style.Frame):
    """
    A simple widget for displaying a single piece of titled, alphanumeric data. By default the title label is packed
    above the data label, but they may be redrawn to support a different layout style (as is done in
    ``LabelledTextBank``).
    """

    def __init__(self, master, title, text="", title_style=None, text_style=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param title: The title.
        :type title: str
        :param text: The initial text for the widget.
        :type text: str
        :param title_style: The style for the title label. Defaults to the style given for the frame (in kwargs).
        :type title_style: Style
        :param text_style: The style for the text label. Defaults to the style given for the frame (in kwargs).
        :type text_style: Style
        :param args: Additional args for the ``style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``style.Frame`` constructor.
        """
        def_style = kwargs.get("style")
        super().__init__(master, *args, **kwargs)

        self.title_var = tk.StringVar(self, title)
        self.text_var = tk.StringVar(self, text)

        self.title_label = style.Label(self, style=(title_style or def_style), textvar=self.title_var)
        self.text_label = style.Label(self, style=(text_style or def_style), textvar=self.text_var)

        self.title_label.pack(fill=tk.BOTH, expand=True)
        self.text_label.pack(fill=tk.BOTH, expand=True)

    @property
    def text(self):
        """
        :return: The current value of the text label.
        :rtype: str
        """
        return self.text_var.get()

    @text.setter
    def text(self, val):
        """
        :param val: New value for the text label.
        :type val: str
        """
        self.text_var.set(val)

    @property
    def title(self):
        """
        :return: The current value of the title label.
        :rtype: str
        """
        return self.title_var.get()

    @title.setter
    def title(self, val):
        """
        :param val: New value for the title label.
        :type val: str
        """
        self.title_var.set(val)


class DockableLabelledText(DockableMixin, LabelledText):
    """Dockable version of ``LabelledText``."""

    def __init__(self, master, title, text="", width=1, height=1, *args, **kwargs):
        super().__init__(master, width, height, title, text, *args, **kwargs)
        # Relay drag events on the labels to the DockableMixin.
        self.bind_drag_on(self.text_label)
        self.bind_drag_on(self.title_label)


class BankBase(style.Frame):
    """Base class for "bank-style" ``BooleanIndicator``s and ``LabelledText``s (i.e. a vertical stack of widgets)."""

    def __init__(self, master, widget_cls, pack_opts=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param widget_cls: The class to use for each bank item.
        :param pack_opts: Options to use when packing each bank item.
        :type pack_opts: dict
        :param args: Additional args for the ``style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``style.Frame`` constructor.
        """
        super().__init__(master, *args, **kwargs)

        self.widgets = []
        """A list of all the widgets in the bank."""

        self.widget_cls = widget_cls
        """The class to use for each bank item."""

        self.pack_opts = pack_opts or {}
        """A dictionary of options (kwargs) to use when packing each bank item."""

        # Set some default options for packing.
        self.pack_opts.setdefault("fill", tk.BOTH)
        self.pack_opts.setdefault("expand", True)
        self.pack_opts.setdefault("ipadx", 2)
        self.pack_opts.setdefault("ipady", 2)
        self.pack_opts.setdefault("padx", 1)
        self.pack_opts.setdefault("pady", 1)

    def add(self, *args, **kwargs):
        """
        Add a widget (of the class specified in the constructor) to the bank.

        :param args: Args for the widget constructor.
        :param kwargs: Kwargs for the widget constructor.
        :return: The newly-added widget.
        """
        widget = self.widget_cls(self, *args, **kwargs)
        self.widgets.append(widget)
        widget.pack(**self.pack_opts)
        return widget

    def remove(self, widget):
        """
        Remove the given widget from the bank. This will fail if the widget is not in the bank.

        :param widget: The widget to remove.
        """
        widget.destroy()
        self.widgets.remove(widget)


class BooleanIndicatorBank(BankBase):
    """``BooleanIndicator`` version of ``BankBase``."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, BooleanIndicator, *args, **kwargs)


class DockableBooleanIndicatorBank(DockableMixin, BooleanIndicatorBank):
    """Dockable version of ``BooleanIndicatorBank``."""

    def __init__(self, master, width=2, height=3, *args, **kwargs):
        super().__init__(master, width, height, *args, **kwargs)

    def add(self, *args, **kwargs):
        bi = super().add(*args, **kwargs)
        # Assure both the frame and label component of the indicator are draggable.
        self.bind_drag_on(bi)
        if bi.label:
            self.bind_drag_on(bi.label)
        return bi


class LabelledTextBank(BankBase):
    """
    ``LabelledText`` version of ``BankBase``.

    The ``LabelledText.title_label`` and ``LabelledText.text_label`` labels are repacked in ``LabelledTextBank.add`` to
    be in a horizontal layout.
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, LabelledText, *args, **kwargs)

    def add(self, *args, **kwargs):
        lt = super().add(*args, **kwargs)
        # Repack the labels horizontally.
        lt.title_label.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        lt.text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return lt


class DockableLabelledTextBank(DockableMixin, LabelledTextBank):
    """Dockable version of ``LabelledTextBank``."""

    def __init__(self, master, width=2, height=3, *args, **kwargs):
        super().__init__(master, width, height, *args, **kwargs)

    def add(self, *args, **kwargs):
        lt = super().add(*args, **kwargs)
        # Assure the frame and both label components of the new widget are draggable.
        self.bind_drag_on(lt)
        self.bind_drag_on(lt.title_label)
        self.bind_drag_on(lt.text_label)
        return lt


class Gyro(style.Canvas):
    """
    A simple gyroscope widget drawn on a canvas. The gyroscope consists of a circle
    """

    # TODO: add label with degrees
    # TODO: style options for canvas items

    def __init__(self, master, radius=100, pointer_frac=3/4, circ_pad=5, auto_resize=True,
                 circ_opts=None, pointer_opts=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param radius: The radius of the circle border in pixels.
        :type radius: int
        :param pointer_frac: How long should the pointer be as a fraction of the circle's radius.
        :type pointer_frac: float
        :param circ_pad: How much padding (in pixels) to add around the circle.
        :type circ_pad: int
        :param auto_resize: Whether or not to automatically resize the circle and pointer when the gyro is allocated
        more screen space
        :type auto_resize: bool
        :param circ_opts: Visual options to use when creating the circle via ``Gyro.create_circle``.
        :type circ_opts: dict
        :param pointer_opts: Visual options to use when creating the pointer via ``tkinter.Canvas.create_line``.
        :type pointer_opts: dict
        :param args: Additional args for the ``style.Canvas`` constructor.
        :param kwargs: Additional kwargs for the ``style.Canvas`` constructor.
        """
        super().__init__(master, *args, **kwargs)

        circ_opts = circ_opts or {}
        circ_opts.setdefault("width", 2)
        self.circle = self.create_circle(0, 0, 0, **circ_opts)
        """The canvas id of the circle."""

        pointer_opts = pointer_opts or {}
        pointer_opts.setdefault("width", 2)
        pointer_opts.setdefault("arrow", tk.LAST)
        self.pointer = self.create_line(0, 0, 0, 0, **pointer_opts)
        """The pointer id of the circle."""

        self.pointer_frac = pointer_frac
        """
        How long should the pointer be as a fraction of the circle's radius. If one updates this, one must call
        ``Gyro.update_point`` afterwards to move the pointer according to the changes made.
        """

        self.circ_pad = circ_pad
        """
        The amount of padding (in pixels) around the circle. If one updates this, one must call
        ``Gyro.update_scroll_region`` afterwards.
        """

        self._radians = 0
        self._radius = None
        if auto_resize:
            # This will be called at least once when this widget is initially drawn, thus the radius needn't be manually
            # initialized.
            self.bind("<Configure>", self._on_configure)
        else:
            # Force an update by manually setting the radius.
            self.radius = radius

    @property
    def radians(self):
        """
        :return: The current angle of the gyro in radians.
        :rtype: float
        """
        return self._radians

    @radians.setter
    def radians(self, val):
        """
        :param val: New angle for the gyro in radians.
        :type val: float
        """
        self._radians = val
        self.update_pointer()

    @property
    def degrees(self):
        """
        :return: The current angle of the gyro in degrees.
        :rtype: float
        """
        return math.degrees(self._radians)

    @degrees.setter
    def degrees(self, val):
        """
        :param val: New angle for the gyro in degrees.
        :type val: float
        """
        self.radians = math.radians(val)

    @property
    def radius(self):
        """
        :return: The radius of the gyro.
        :rtype: int
        """
        return self._radius

    @radius.setter
    def radius(self, val):
        """
        :param val: New radius for the gyro in pixels.
        :type val: int
        """
        self._radius = val
        self.coords(self.circle, *self.circ_to_oval(0, 0, val))
        self.update_pointer()
        self.update_scroll_region()

    def update_pointer(self):
        """Move the pointer to reflect a change made to ``Gyro.pointer_frac`` or the radius."""
        x = -self.pointer_frac * self.radius * math.cos(self._radians + math.pi / 2)
        y = -self.pointer_frac * self.radius * math.sin(self._radians + math.pi / 2)
        self.coords(self.pointer, 0, 0, x, y)

    def update_scroll_region(self):
        """Change the canvas's scrollregion to reflect a change made to ``Gyro.circ_pad`` or the radius."""
        self.configure(scrollregion=(-self._radius - self.circ_pad,
                                     -self._radius - self.circ_pad,
                                     self._radius + self.circ_pad,
                                     self._radius + self.circ_pad))

    def _on_configure(self, event):
        """
        Internal method used as the callback for "<Configure>" events if the ``auto_resize`` parameter was set in the
        constructor. This method updates the radius of the gyro according to any new space allocated/removed by resizing
        this gyro's parent widget.

        :param event: The tkinter event object.
        """
        self.radius = (min(event.width, event.height) - 2 * self.circ_pad) / 2

    def create_circle(self, x, y, r, **kwargs):
        """
        Wrapper around ``tkinter.Canvas.create_oval`` to make constructing circles more intuitive.

        :param x: The x coordinate of the circle's center.
        :type x: int
        :param y: The y coordinate of the circle's center.
        :type y: int
        :param r: The radius of the circle.
        :type r: int
        :param kwargs: Additional (visual) options for ``tkinter.Canvas.create_oval``.
        :return: The canvas id of the new circle.
        """
        return self.create_oval(*self.circ_to_oval(x, y, r), **kwargs)

    @staticmethod
    def circ_to_oval(x, y, r):
        """
        Convert the given information defining a circle into the information required to define an oval in tkinter.

        :param x: The x coordinate of the circle's center.
        :type x: int
        :param y: The y coordinate of the circle's center.
        :type y: int
        :param r: The radius of the circle.
        :type r: int
        :return: The values needed to construct the circle in tkinter as a 4-tuple of integers.
        :rtype: tuple
        """
        return x - r, y - r, x + r, y + r


class DockableGyro(DockableMixin, Gyro):
    """Dockable version of ``Gyro``."""
    pass


class NTBrowser(style.Frame):
    """
    TODO
    """

    PARENT_DIR = ".."
    """How to represent the parent directory of a subtable."""

    TABLE_FORMAT = "[T] {}"
    """Format string for tables in the ``NTBrowser.key_listbox`` listbox."""

    ENTRY_FORMAT = "[E] {}"
    """Format string for entries in the ``NTBrowser.key_listbox`` listbox."""

    BLANK = "-"
    """How to represent an invalid value (i.e. for a table) in the ``NTBrowser.value_listbox`` listbox."""

    INFO_DATA_WIDTH = 20
    """The initial width in characters for the ``tkinter.Text`` widget in the entry info popups."""

    INFO_DATA_HEIGHT = 5
    """The initial height in characters for the ``tkinter.Text`` widget in the entry info popups."""

    def __init__(self, master, root_table,
                 scrollbar_style=None,
                 listbox_style=None,
                 header_style=None,
                 label_style=None,
                 entry_style=None,
                 button_style=None,
                 info_text_style=None,
                 *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param root_table: The top-level networktables table to model in this widget.
        :type root_table: networktables.networktable.NetworkTable
        :param scrollbar_style:  The style for the scrollbar. Defaults to the style given for the frame (in kwargs).
        :type scrollbar_style: spookyconsole.gui.style.Style
        :param listbox_style:  The style for the listboxes. Defaults to the style given for the frame (in kwargs).
        :type listbox_style: spookyconsole.gui.style.Style
        :param header_style: The style for the listbox headers. Defaults to the style given for the frame (in kwargs).
        :type header_style: spookyconsole.gui.style.Style
        :param label_style: The style for the entry label. Defaults to the style given for the frame (in kwargs).
        :type label_style: spookyconsole.gui.style.Style
        :param entry_style: The style for the entry. Defaults to the style given for the frame (in kwargs).
        :type entry_style: spookyconsole.gui.style.Style
        :param button_style: The style for the button. Defaults to the style given for the frame (in kwargs).
        :type button_style: spookyconsole.gui.style.Style
        :param info_text_style: The style for the info popup text widget. Defaults to the style given for the frame (in
        kwargs).
        :type info_text_style: spookyconsole.gui.style.Style
        :param args: Additional args for the ``spookyconsole.gui.style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``spookyconsole.gui.style.Frame`` constructor.
        """
        # Assure all the subwidget styles default to the frame style (which may itself be undefined).
        def_style = kwargs.get("style")
        scrollbar_style = scrollbar_style or def_style
        listbox_style = listbox_style or def_style
        header_style = header_style or def_style
        label_style = label_style or def_style
        entry_style = entry_style or def_style
        button_style = button_style or def_style

        super().__init__(master, *args, **kwargs)

        self.root_table = root_table
        """The top-level ``networktables.networktable.NetworkTable`` to model in this widget."""

        self.hierarchy = deque((root_table,))
        """
        This holds the current path into the root table so we may navigate through the tables by appending and popping
        to the end of the deque.
        """

        self._last_table_idx = None
        """"""

        self._items = []
        """"""

        self._curr_indices = None
        """"""

        self._curr_scroll_row = 0
        """"""

        self._entry_popup = popup.PopupManager(self, title_fmt="Info: {}", style=def_style, resizeable=(True, True))
        """"""

        # Save only the subwidget styles that are accessed later as instance attributes.
        self._header_style = header_style
        self._label_style = label_style
        self._button_style = button_style
        self._info_text_style = info_text_style or def_style

        # Construct the "upper" subwidgets.
        self.scrollbar = style.Scrollbar(self, style=scrollbar_style, command=self._merged_yview)
        self.key_label = style.Label(self, style=header_style, text="KEY")
        self.key_listbox = style.Listbox(self, style=listbox_style, selectmode=tk.EXTENDED,
                                         yscrollcommand=self.scrollbar.set)
        self.value_label = style.Label(self, style=header_style, text="VALUE")
        self.value_listbox = style.Listbox(self, style=listbox_style, selectmode=tk.EXTENDED,
                                           yscrollcommand=self.scrollbar.set)

        # Construct the "lower" subwidgets.
        self.lower_frame = style.Frame(self, style=def_style)
        self.insert_label = style.Label(self.lower_frame, style=label_style, text="INSERT:")
        self.insert_entry = style.Entry(self.lower_frame, style=entry_style, state=tk.DISABLED)
        self.insert_button = style.Button(self.lower_frame, style=button_style,
                                          command=self._insert_callback, text="Enter")
        self.reload_button = style.Button(self.lower_frame, style=button_style,
                                          command=self.reload, text="Reload")

        # Make only the listboxes resizeable, and make them equally resizeable.
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Make only the entry resizable in the lower frame.
        self.lower_frame.grid_columnconfigure(1, weight=1)

        # Grid the "upper" subwidgets.
        self.key_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.value_label.grid(row=0, column=1, sticky=tk.NSEW)
        self.key_listbox.grid(row=1, column=0, sticky=tk.NSEW)
        self.value_listbox.grid(row=1, column=1, sticky=tk.NSEW)
        self.scrollbar.grid(row=1, column=2, sticky=tk.NS)

        # Grid the "lower" subwidgets.
        self.insert_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.insert_entry.grid(row=0, column=1, sticky=tk.NSEW)
        self.insert_button.grid(row=0, column=2, sticky=tk.NSEW)
        self.reload_button.grid(row=0, column=3, sticky=tk.NSEW)
        self.lower_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)

        # Bind scroll events on the listboxes.
        self.key_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.value_listbox.bind("<MouseWheel>", self._wheel_scroll)
        # Bind double-click events on the listboxes.
        self.key_listbox.bind("<Double-Button-1>", self._key_double_click_callback)
        self.value_listbox.bind("<Double-Button-1>", self._value_double_click_callback)
        # Bind select events on the listboxes.
        self.key_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        self.value_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        # Bind the return key on the entry.
        self.insert_entry.bind("<Return>", self._insert_callback)

        # Initialize the table by populating it with the root table.
        self._populate(self.root_table)

    def reload(self):
        self._populate(self.hierarchy[-1])

    def reload_when_connected(self, inst, poll_ms=500):
        if inst.isConnected():
            self.reload()
        else:
            self.after(poll_ms, utils.named_partial(self.reload_when_connected, inst, poll_ms))

    def _merged_yview(self, *args):
        self._curr_scroll_row = round(float(args[1]) * len(self._items))
        self.key_listbox.yview(*args)
        self.value_listbox.yview(*args)

    def _wheel_scroll(self, event):
        lower_scroll, upper_scroll = self.scrollbar.get()
        if (lower_scroll != 0 and event.delta > 0) or (upper_scroll != 1 and event.delta < 0):
            self._curr_scroll_row += int(math.copysign(1, -event.delta))
            diff = int(math.copysign(4, -event.delta))
            self.key_listbox.yview(self._curr_scroll_row + (diff if self.key_listbox is not event.widget else 0))
            self.value_listbox.yview(self._curr_scroll_row + (diff if self.value_listbox is not event.widget else 0))

    def _key_double_click_callback(self, _):
        if len(self._curr_indices) != 1:
            return  # TODO: Some sort of warning or error
        idx = self._curr_indices[0]
        if self.key_listbox.get(idx) == self.PARENT_DIR:
            self.hierarchy.pop()
            self._populate(self.hierarchy[-1])
        elif idx <= self._last_table_idx:
            table = self._items[idx]
            self.hierarchy.append(table)
            self._populate(table)
        else:
            self._create_entry_popup(idx)

    def _value_double_click_callback(self, _):
        if len(self._curr_indices) != 1:
            return  # TODO: Some sort of warning or error
        idx = self._curr_indices[0]
        if idx <= self._last_table_idx:
            return  # TODO: Some sort of warning or error
        self._create_entry_popup(idx)

    def _create_entry_popup(self, idx):
        entry = self._items[idx]

        frame = style.Frame(self._entry_popup, style=self._style)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        style.Label(frame, style=self._header_style, text="TYPE:").grid(row=0, column=0)
        style.Label(frame, style=self._label_style, text=ntutils.type_constant_to_str(entry.getType()))\
            .grid(row=0, column=1)

        style.Label(frame, style=self._header_style, text="DATA:").grid(row=1, column=0)
        data = style.Text(frame, style=self._info_text_style, width=self.INFO_DATA_WIDTH, height=self.INFO_DATA_HEIGHT)
        data.insert(tk.END, str(entry.value))
        data.configure(state=tk.DISABLED)
        data.grid(row=1, column=1, sticky=tk.NSEW)

        if self._entry_popup.popup_open:
            self._entry_popup.close_current_popup()
        self._entry_popup.create(frame, entry.getName())

    def _populate(self, table):
        self._curr_scroll_row = 0
        self._disable_entry()
        self._clear()
        self._last_table_idx = -1
        if table is not self.root_table:
            self._append_pair(self.PARENT_DIR, self.BLANK, None)
            self._last_table_idx += 1
        for subtable in table.getSubTables():
            self._append_pair(self.TABLE_FORMAT.format(subtable), self.BLANK, table.getSubTable(subtable))
            self._last_table_idx += 1
        for key in table.getKeys():
            entry = table.getEntry(key)
            self._append_pair(self.ENTRY_FORMAT.format(key), str(entry.value), entry)

    def _append_pair(self, key, value, item):
        self._items.append(item)
        self.key_listbox.insert(tk.END, key)
        self.value_listbox.insert(tk.END, value)

    def _clear(self):
        self._items = []
        self.key_listbox.delete(0, tk.END)
        self.value_listbox.delete(0, tk.END)

    def _insert_callback(self, _=None):
        try:
            value = ntutils.type_cast(self.insert_entry.get(), self._items[self._curr_indices[0]].getType())
            for idx in self._curr_indices:
                ntutils.set_entry_by_type(self._items[idx], value)
            self.reload()
        except ValueError as e:
            popup.dialog("Type Error", "Error: {}".format(str(e)), popup.BUTTONS_OK,
                         frame_style=self._style, message_style=self._label_style, button_style=self._button_style)

    def _disable_entry(self):
        self.insert_entry.delete(0, tk.END)
        self.insert_entry.configure(state=tk.DISABLED)
        self.insert_button.configure(state=tk.DISABLED)

    def _enable_entry(self):
        self.insert_entry.configure(state=tk.NORMAL)
        self.insert_button.configure(state=tk.NORMAL)

    def _listbox_select_callback(self, _):
        self._curr_indices = self.key_listbox.curselection() or self.value_listbox.curselection()
        if self._curr_indices:
            kind = None
            for idx in self._curr_indices:
                if idx <= self._last_table_idx:
                    break
                if kind is None:
                    kind = self._items[idx].getType()
                elif self._items[idx].getType() != kind:
                    break
            else:
                self._enable_entry()
                return
        self._disable_entry()


class DockableNTBrowser(DockableMixin, NTBrowser):
    """Dockable version of ``NTBrowser``."""

    def __init__(self, master, table, width=5, height=5, *args, **kwargs):
        super().__init__(master, width, height, table, *args, **kwargs)
        # Make each subwidget draggable.
        self.bind_drag_on(self.key_listbox)
        self.bind_drag_on(self.value_listbox)
        self.bind_drag_on(self.key_label)
        self.bind_drag_on(self.value_label)
        self.bind_drag_on(self.insert_label)


# TODO: Motor monitor, kinematics info display
# TODO: Power info display
# TODO: Log output?
# TODO: Camera?
# TODO: start working on complementary code in spooky-lib
# TODO: start writing actual click command code to interface with gui
# TODO: analysis tools for recorded msgpack data?
# TODO: args coming after a long chain of pos args with default vals
# TODO: make all types absolute in docstrings
