
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
    A rectangular widget for displaying a boolean value indicated by two different colours. The indicator may have a
    label on it. Also, the indicator can optionally be "mutable", meaning it can be clicked by the user to toggle it.
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
        :type label_style: spookyconsole.gui.style.Style
        :param args: Additional args for the ``style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``style.Frame`` constructor.
        """
        super().__init__(master, *args, **kwargs)
        self.on_colour = on_colour
        self.off_colour = off_colour

        # Make the label resizable.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = None
        if text:
            self.label = style.Label(self, style=(label_style or kwargs.get("style")), text=text)
            self.label.grid()

        if mutable:
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
        Internal method used as the callback for write events on ``BooleanIndicator.var``. This changes the colour of
        the frame (and, if it exists, the label) according to the new state of the variable.
        """
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
        # If a label was given for the indicator, assure that it relays drag events to the DockableMixin.
        if self.label:
            self.bind_drag_on(self.label)


class LabelledText(style.Frame):
    """
    A simple widget for displaying a single piece of titled, alphanumeric data. The title label is packed above the data
    label.
    """

    def __init__(self, master, title, text="", title_style=None, text_style=None, *args, **kwargs):
        """
        :param master: The master tkinter widget.
        :param title: The title of the data.
        :type title: str
        :param text: The initial text for the widget.
        :type text: str
        :param title_style: The style for the title label. Defaults to the style given for the frame (in kwargs).
        :type title_style: spookyconsole.gui.style.Style
        :param text_style: The style for the text label. Defaults to the style given for the frame (in kwargs).
        :type text_style: spookyconsole.gui.style.Style
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
        self.widgets.remove(widget)
        widget.destroy()


class BooleanIndicatorBank(BankBase):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, BooleanIndicator, *args, **kwargs)


class DockableBooleanIndicatorBank(DockableMixin, BooleanIndicatorBank):

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

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, LabelledText, *args, **kwargs)

    def add(self, *args, **kwargs):
        lt = super().add(*args, **kwargs)
        # Repack the labels horizontally.
        lt.title_label.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        lt.text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return lt


class DockableLabelledTextBank(DockableMixin, LabelledTextBank):

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
    A simple gyroscope widget drawn on a canvas. The gyroscope consists of a circle and a pointer. The pointer is
    updated automatically as the angle of the gyroscope is set. If ``auto_resize`` is set in the constructor, the circle
    and pointer will automatically resize as the gyro is allocated more or less screen space.
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
        more screen space.
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
            # _on_configure will be called at least once when this widget is initially drawn, thus the radius needn't be
            # manually initialized.
            self.bind("<Configure>", self._on_configure)
        else:
            # Force an update by setting the radius property.
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
        :return: The radius of the gyro in pixels.
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
        pointer_length = -self.pointer_frac * self.radius
        # Add pi/2 to the angle because we consider 0 radians to be pi/2 in standard position.
        x = pointer_length * math.cos(self._radians + math.pi / 2)
        y = pointer_length * math.sin(self._radians + math.pi / 2)
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
    pass


class NTBrowser(style.Frame):
    """
    A widget for displaying the contents (both subtables and entries) of a ``networktables.networktable.NetworkTable``.
    This widget is navigable, meaning subtables of the given "root table" (and subtables of those subtables, etcetera)
    can be interactively explored.

    This widget consists of two side-by-side ``tkinter.Listbox``s, one to display the name of a subtable or entry, and
    the other to display the value corresponding to an entry (the value of a row in the listboxes representing a
    subtable is simply filled in by ``NTBrowser.BLANK``). Both listbox columns are labeled and scrollable via a shared
    scrollbar.

    Below the listboxes lies an ``tkinter.entry`` (hereby to be refered to as a "tkentry" to avoid confusion) and an
    "Enter" button. The tkentry can be used to set the value of a selected entry in the currently displayed table: once
    the desired data is entered into the tkentry, the user must either click the "Enter" button or press <Return> on the
    keyboard while the tkentry has keyboard focus to set the networktables entry. Whether it is the key or value listbox
    that has the selection is irrelevant. Multiple entries can be set at the same time if they all have the same type by
    selecting them using the <Shift> and <Ctrl> keys. If an invalid selection of listbox rows is encountered (e.g. if a
    subtable is selected or if multiple entries with varying types are selected), the tkentry will be disabled. An error
    popup window will appear if the given data string in the tkentry cannot be converted to the entry's type.

    To navigate to a subtable, double-click it in the key listbox. The parent table of the currently displayed table can
    be returned to by double clicking the top row in the key listbox, which is by default labelled ".." (although this
    can be changed by setting ``NTBrowser.PARENT_DIR``).

    Double-clicking on an entry in the listboxes will cause a resizable popup window to appear with the entry's type and
    value in it. (This is mainly so that entries with long data strings can be viewed in full).

    The subtables, entries, and entry values in the listboxes do not update automatically (except after one of the
    entry's values is manually changed); the "Reload" button, which is beside the "Enter" button, must be clicked to
    force a reload. The listboxes can also be updated programmatically using the ``NTBrowser.reload`` method.

    If an ``NTBrowser`` is constructed while a ``networktables.instance.NetworkTablesInstance`` is suspected to be still
    in the process of connecting, one might want to call ``NTBrowser.reload_when_connected`` after constructing the
    ``NTBrowser`` object.
    """

    # TODO: make text in labels controllable?
    # TODO: have a label show the current path into the table

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
        :param label_style: The style for the tk entry label. Defaults to the style given for the frame (in kwargs).
        :type label_style: spookyconsole.gui.style.Style
        :param entry_style: The style for the tk entry. Defaults to the style given for the frame (in kwargs).
        :type entry_style: spookyconsole.gui.style.Style
        :param button_style: The style for the button. Defaults to the style given for the frame (in kwargs).
        :type button_style: spookyconsole.gui.style.Style
        :param info_text_style: The style for the info popup Text widget. Defaults to the style given for the frame (in
        kwargs).
        :type info_text_style: spookyconsole.gui.style.Style
        :param args: Additional args for the ``spookyconsole.gui.style.Frame`` constructor.
        :param kwargs: Additional kwargs for the ``spookyconsole.gui.style.Frame`` constructor.
        """
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
        """
        Stores the index of the last subtable in the ``NTBrowser.value_listbox`` listbox (ALL the tables appear before
        ALL the entries).
        """

        self._items = []
        """
        Stores a list of the ``networktables.networktable.NetworkTable``s and ``networktables.entry.NetworkTableEntry``s
        in the currently displayed (sub)table.
        """

        self._curr_indices = None
        """Stores the listbox indices currently selected by the user."""

        self._curr_scroll_row = 0
        """
        Stores the first visible listbox row. This attribute is made necessary by weird behaviour when using one
        scrollbar to control two listboxes (see ``NTBrowser._wheel_scroll`` for more information).
        """

        self._entry_popup = popup.PopupManager(self, title_fmt="Info: {}", style=def_style, resizeable=(True, True))
        """The ``spookyconsole.gui.popup.PopupManager`` for the extra info window on networktables entries."""

        # Save only the subwidget styles that are accessed later as instance attributes.
        self._header_style = header_style
        self._label_style = label_style
        self._button_style = button_style
        self._info_text_style = info_text_style or def_style

        # Construct all the subwidgets.
        self.scrollbar = style.Scrollbar(self, style=scrollbar_style, command=self._merged_yview)
        self.key_label = style.Label(self, style=header_style, text="KEY")
        self.key_listbox = style.Listbox(self, style=listbox_style, selectmode=tk.EXTENDED,
                                         yscrollcommand=self.scrollbar.set)
        self.value_label = style.Label(self, style=header_style, text="VALUE")
        self.value_listbox = style.Listbox(self, style=listbox_style, selectmode=tk.EXTENDED,
                                           yscrollcommand=self.scrollbar.set)
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

        # Grid all the subwidgets.
        self.key_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.value_label.grid(row=0, column=1, sticky=tk.NSEW)
        self.key_listbox.grid(row=1, column=0, sticky=tk.NSEW)
        self.value_listbox.grid(row=1, column=1, sticky=tk.NSEW)
        self.scrollbar.grid(row=1, column=2, sticky=tk.NS)
        self.insert_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.insert_entry.grid(row=0, column=1, sticky=tk.NSEW)
        self.insert_button.grid(row=0, column=2, sticky=tk.NSEW)
        self.reload_button.grid(row=0, column=3, sticky=tk.NSEW)
        self.lower_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)

        # Bind events on subwidgets.
        self.key_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.value_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.key_listbox.bind("<Double-Button-1>", self._key_double_click_callback)
        self.value_listbox.bind("<Double-Button-1>", self._value_double_click_callback)
        self.key_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        self.value_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        self.insert_entry.bind("<Return>", self._insert_callback)

        # Initialize the table by populating it with the root table.
        self._populate(self.root_table)

    def reload(self):
        """Reload the data in the listboxes to reflect any changes on the networktables server."""
        self._populate(self.hierarchy[-1])

    def reload_when_connected(self, inst, poll_ms=500):
        """
        Wait until the given networktables instance successfully connects and then populate the listboxes with data.
        This should be called after the ``NTBrowser`` is constructed if the networktables instance containing the root
        table is suspected to be disconnected.

        :param inst: The instance to check for connectivity on.
        :type inst: networktables.instance.NetworkTablesInstance
        :param poll_ms: How long to wait in between connectivity checks.
        :type poll_ms: int
        """
        if inst.isConnected():
            self.reload()
        else:
            self.after(poll_ms, utils.named_partial(self.reload_when_connected, inst, poll_ms))

    def _merged_yview(self, *args):
        """A merged yview function for both listboxes so that they can both be controlled via a single scrollbar."""
        self._curr_scroll_row = round(float(args[1]) * len(self._items))
        self.key_listbox.yview(*args)
        self.value_listbox.yview(*args)

    def _wheel_scroll(self, event):
        """
        Internal method used as the callback for "<MouseWheel>" events.

        :param event: The tkinter event object.
        """
        # For some unknown reason, when using a single scrollbar to control two listboxes they get out of sync by
        # exactly four listbox rows, with the one being hovered over while scrolling being ahead of the other.
        # Therefore, below we have some (seemingly) effective albeit strange logic to make sure both scrollbars stay in
        # sync.

        lower_scroll, upper_scroll = self.scrollbar.get()
        # Only make any changes to _curr_scroll_row if the given scroll event would actually make any change to the
        # listboxs (i.e. if we're not at the top of the listboxes and scrolling up nor at the bottom of the listboxes
        # and scrolling down).
        if (lower_scroll != 0 and event.delta > 0) or (upper_scroll != 1 and event.delta < 0):
            # Increment or decrement _curr_scroll_row according to the direction of the scroll event.
            self._curr_scroll_row += int(math.copysign(1, -event.delta))
            # diff is the difference in rows between the "ahead" listbox and the "behind" one. It always (seemingly
            # arbitrarily) has magnitude 4.
            diff = int(math.copysign(4, -event.delta))
            # Set the yviews of the listboxes, adding the difference to the correct one.
            self.key_listbox.yview(self._curr_scroll_row + (diff if self.key_listbox is not event.widget else 0))
            self.value_listbox.yview(self._curr_scroll_row + (diff if self.value_listbox is not event.widget else 0))

    def _key_double_click_callback(self, _):
        """
        Internal method used as the callback for "<Double-Button-1>" events on the ``NTBrowser.key_listbox`` listbox.
        """
        # Theoretically, it should be impossible to double click with more than one row selected, but just in case...
        if len(self._curr_indices) != 1:
            return  # TODO: Some sort of warning or error
        idx = self._curr_indices[0]
        if self.key_listbox.get(idx) == self.PARENT_DIR:  # If the selected row is the parent table.
            self.hierarchy.pop()
            self._populate(self.hierarchy[-1])
        elif idx <= self._last_table_idx:  # If the selected row is any other table.
            table = self._items[idx]
            self.hierarchy.append(table)
            self._populate(table)
        else:  # If the selected row is an entry.
            self._create_entry_popup(idx)

    def _value_double_click_callback(self, _):
        """
        Internal method used as the callback for "<Double-Button-1>" events on the ``NTBrowser.value_listbox`` listbox.
        """
        # Theoretically, it should be impossible to double click with more than one row selected, but just in case...
        if len(self._curr_indices) != 1:
            return  # TODO: Some sort of warning or error
        idx = self._curr_indices[0]
        # If the selected row corresponds to the value of a table (which is nonsense), do nothing.
        if idx <= self._last_table_idx:
            return  # TODO: Some sort of warning or error
        # Otherwise, the selected row in the listbox must be an entry, so display the entry info popup window.
        self._create_entry_popup(idx)

    def _create_entry_popup(self, idx):
        """
        Create a popup window displaying the type and value of the entry corresponding to the given index.

        :param idx: The index in the ``NTBrowser._items`` list for the entry to display in the popup window.
        :type idx: int
        """
        entry = self._items[idx]

        frame = style.Frame(self._entry_popup, style=self._style)

        # Make only the Text widget (which holds the entry's value) resizeable.
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        style.Label(frame, style=self._header_style, text="TYPE:").grid(row=0, column=0)
        style.Label(frame, style=self._label_style, text=ntutils.type_constant_to_str(entry.getType()))\
            .grid(row=0, column=1)

        style.Label(frame, style=self._header_style, text="DATA:").grid(row=1, column=0)
        data = style.Text(frame, style=self._info_text_style, width=self.INFO_DATA_WIDTH, height=self.INFO_DATA_HEIGHT)
        data.insert(tk.END, str(entry.value))
        # Disable the text widget so it cannot be edited.
        data.configure(state=tk.DISABLED)
        data.grid(row=1, column=1, sticky=tk.NSEW)

        # Forcefully close an already-open popup window, should one exists. PopupManager prevents having more than one
        # popup open at once and queues any subsequent popups, which would be weird in this case.
        if self._entry_popup.popup_open:
            self._entry_popup.close_current_popup()

        # Create the popup window with the entry's name as the title of the window.
        self._entry_popup.create(frame, entry.getName())

    def _populate(self, table):
        """
        Populate the listboxes with subtables, entries, and entry values from the given table. If the given table is not
        the root table, the parent table is added first. Secondly, all the subtables of the given table are added.
        Finally, all the entries in the given table are added.

        :param table: The networktable to populate the listboxes with.
        :type table: networktables.networktable.NetworkTable
        """
        # Repopulating the listboxes will reset the scroll.
        self._curr_scroll_row = 0
        # Repopulating the listboxes will reset the selection, so make sure the entry defaults to disabled.
        self._disable_entry()
        self._clear()
        # Initialize the _last_table_idx to -1 because the listbox rows are zero-indexed and each table added to the
        # listboxes will increment _last_table_idx.
        self._last_table_idx = -1
        # Add a parent table row to the listboxes if the given table is not the root table.
        if table is not self.root_table:
            self._append_row(self.PARENT_DIR, self.BLANK, None)
            self._last_table_idx += 1
        # Iterate through the given table's subtables and add each one to the listboxes.
        for subtable in table.getSubTables():
            self._append_row(self.TABLE_FORMAT.format(subtable), self.BLANK, table.getSubTable(subtable))
            self._last_table_idx += 1
        # Iterate through the given table's entries and add each one to the listboxes.
        for key in table.getKeys():
            entry = table.getEntry(key)
            self._append_row(self.ENTRY_FORMAT.format(key), str(entry.value), entry)

    def _append_row(self, key, value, item):
        """
        Add the given key and value to the listboxes and add the given networktables table or entry to the
        ``NTBrowser._items`` list.

        :param key: The key of the table or entry.
        :type key: str
        :param value: The value of the entry or the ``NTBrowser.BLANK`` filler string for tables.
        :type value: str
        :param item: The table or entry corresponding to the given key and value.
        """
        self._items.append(item)
        self.key_listbox.insert(tk.END, key)
        self.value_listbox.insert(tk.END, value)

    def _clear(self):
        """Clear both listboxes and the items list."""
        self._items = []
        self.key_listbox.delete(0, tk.END)
        self.value_listbox.delete(0, tk.END)

    def _insert_callback(self, _=None):
        """
        Internal method used as the callback for "<Return>" events on the ``NTBrowser.insert_entry`` and command on the
        ``NTBrowser.insert_button``. This sets the value on the selected entries to whatever is in the tkinter entry.
        """
        try:
            value = ntutils.type_cast(self.insert_entry.get(), self._items[self._curr_indices[0]].getType())
            for idx in self._curr_indices:
                ntutils.set_entry_by_type(self._items[idx], value)
            # Reload when done to assure the new data appears in the listboxes.
            self.reload()
        except ValueError as e:
            # If an error occurred while trying to cast the given string to the type expected by the selected entries,
            # create a popup window telling the user of the error.
            popup.dialog("Type Error", "Error: {}".format(str(e)), popup.BUTTONS_OK,
                         frame_style=self._style, message_style=self._label_style, button_style=self._button_style)

    def _disable_entry(self):
        """Clear the entry and disable the entry and button, making them unable to be interacted with."""
        self.insert_entry.delete(0, tk.END)
        self.insert_entry.configure(state=tk.DISABLED)
        self.insert_button.configure(state=tk.DISABLED)

    def _enable_entry(self):
        """Enable the entry and button, allowing them to be interacted with."""
        self.insert_entry.configure(state=tk.NORMAL)
        self.insert_button.configure(state=tk.NORMAL)

    def _listbox_select_callback(self, _):
        """
        Internal method used as the callback for "<<ListboxSelect>>" events on the listboxes. This method enables or
        disabled the entry as appropriate to the new data selection and sets ``NTBrowser._curr_indices``.
        """
        self._curr_indices = self.key_listbox.curselection() or self.value_listbox.curselection()
        if self._curr_indices:
            kind = None
            for idx in self._curr_indices:
                # Break if any one of the selected rows is a table.
                if idx <= self._last_table_idx:
                    break
                if kind is None:
                    kind = self._items[idx].getType()
                # If any two entries in the selection disagree in type, break (and, hence, disable the entry).
                elif self._items[idx].getType() != kind:
                    break
            else:
                # Only enable the entry if the for loop wasn't broken out of.
                self._enable_entry()
                return
        self._disable_entry()


class DockableNTBrowser(DockableMixin, NTBrowser):

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
