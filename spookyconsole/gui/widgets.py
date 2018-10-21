
"""
TODO
"""

import tkinter as tk
import math
from collections import deque
from .core import DockableMixin
from .. import ntutils


class DockableLabel(DockableMixin, tk.Label):
    pass


class DockableEntry(DockableMixin, tk.Entry):
    pass


class DockableCheckbutton(DockableMixin, tk.Checkbutton):
    pass


class DockableLabelFrame(DockableMixin, tk.LabelFrame):
    pass


class DockableButton(DockableMixin, tk.Button):
    pass


class DockableFrame(DockableMixin, tk.Frame):
    pass


class DockableListbox(DockableMixin, tk.Listbox):
    pass


class DockableRadiobutton(DockableMixin, tk.Radiobutton):
    pass


class DockableScale(DockableMixin, tk.Scale):
    pass


class DockableSpinbox(DockableMixin, tk.Spinbox):
    pass


class DockableCanvas(DockableMixin, tk.Canvas):
    pass


class DockableText(DockableMixin, tk.Text):
    pass


class BooleanIndicator(tk.Frame):

    def __init__(self, master, text="", mutable=False, on_colour="green", off_colour="red", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.var = tk.BooleanVar(self)
        self.on_colour = on_colour
        self.off_colour = off_colour

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.label = None
        if text:
            self.label = tk.Label(self, text=text)
            self.label.grid()

        if mutable:
            self.bind("<Button-1>", self._on_click)
            if self.label:
                self.label.bind("<Button-1>", self._on_click)

        self.var.trace_add("write", self._on_change)
        self.value = True

    @property
    def value(self):
        return self.var.get()

    @value.setter
    def value(self, val):
        self.var.set(val)

    def _on_change(self, *_):
        colour = self.on_colour if self.value else self.off_colour
        self.configure(bg=colour)
        if self.label:
            self.label.configure(bg=colour)

    def _on_click(self, _):
        self.value = not self.value


class DockableBooleanIndicator(DockableMixin, BooleanIndicator):

    def __init__(self, master, width=1, height=1, *args, **kwargs):
        super().__init__(master, width, height, *args, **kwargs)
        if self.label:
            self.bind_drag_on(self.label)


class Gyro(tk.Canvas):

    # TODO: add label with degrees

    def __init__(self, master, radius=100, pointer_frac=3/4, circ_pad=5, auto_resize=True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.circle = self.create_circle(0, 0, 0, width=2, fill="#808080")
        self.pointer = self.create_line(0, 0, 0, 0, arrow=tk.LAST, width=2)
        self._radians = 0
        self._radius = None
        self.pointer_frac = pointer_frac
        self.circ_pad = circ_pad
        if auto_resize:
            self.bind("<Configure>", self._on_configure)
        else:
            self.radius = radius

    @property
    def radians(self):
        return self._radians

    @radians.setter
    def radians(self, val):
        self._radians = val
        self.update_pointer()

    @property
    def degrees(self):
        return math.degrees(self._radians)

    @degrees.setter
    def degrees(self, val):
        self.radians = math.radians(val)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.coords(self.circle, *self.circ_to_oval(0, 0, val))
        self.update_pointer()
        self.configure(scrollregion=(-val - self.circ_pad,
                                     -val - self.circ_pad,
                                     val + self.circ_pad,
                                     val + self.circ_pad))

    def update_pointer(self):
        x = -self.pointer_frac * self.radius * math.cos(self._radians + math.pi / 2)
        y = -self.pointer_frac * self.radius * math.sin(self._radians + math.pi / 2)
        self.coords(self.pointer, 0, 0, x, y)

    def _on_configure(self, event):
        self.radius = (min(event.width, event.height) - 2 * self.circ_pad) / 2

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(*self.circ_to_oval(x, y, r), **kwargs)

    @staticmethod
    def circ_to_oval(x, y, r):
        return x - r, y - r, x + r, y + r


class DockableGyro(DockableMixin, Gyro):
    pass


class Popup(tk.Toplevel):
    # TODO: Put in tkutils file
    def __init__(self, master, message, title, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title(title)
        self.minsize(300, 100)
        self.focus_get()

        tk.Label(self, text=message).pack()


from networktables.instance import NetworkTablesInstance
import random


class TableSim:

    class EntrySim:

        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.type = random.choice([NetworkTablesInstance.EntryTypes.BOOLEAN,
                                       NetworkTablesInstance.EntryTypes.DOUBLE,
                                       NetworkTablesInstance.EntryTypes.STRING,
                                       NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY,
                                       NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY,
                                       NetworkTablesInstance.EntryTypes.STRING_ARRAY])

        def getName(self):
            return self.key

        def getType(self):
            return self.type

        def setBoolean(self, val):
            self.value = val

        setDouble = setString = setBooleanArray = setDoubleArray = setStringArray = setBoolean

    PATH_SEPARATOR = '/'

    def __init__(self, data, path=PATH_SEPARATOR):
        self.data = data
        self.path = path

        for k, v in self.data.items():
            if not self.is_sub_table(v) and not self.is_entry(v):
                self.data[k] = self.EntrySim(k, v)

    def getEntry(self, key):
        ret = self.data[key]
        assert self.is_entry(ret)
        return ret

    def getSubTable(self, key):
        ret = self.data[key]
        assert self.is_sub_table(ret)
        return TableSim(ret, self.path + key + self.PATH_SEPARATOR)

    def getKeys(self):
        return [key for key, value in self.data.items() if isinstance(value, TableSim.EntrySim)]

    def getSubTables(self):
        return [key for key, value in self.data.items() if isinstance(value, dict)]

    def containsKey(self, key):
        try:
            return isinstance(self.data[key], TableSim.EntrySim)
        except KeyError:
            return False

    def containsSubTable(self, key):
        try:
            return isinstance(self.data[key], dict)
        except KeyError:
            return False

    @staticmethod
    def is_sub_table(data):
        return isinstance(data, dict)

    @staticmethod
    def is_entry(data):
        return isinstance(data, TableSim.EntrySim)


class NTBrowser(tk.Frame):

    PARENT_DIR = ".."
    TABLE_FORMAT = "[T] {}"
    ENTRY_FORMAT = "[E] {}"
    BLANK = "-"
    SCROLL_SCALE = 1/120

    class EntryPopup(tk.Toplevel):

        DATA_HEIGHT = 1
        DATA_WIDTH = 40

        def __init__(self, master, entry):
            super().__init__(master)
            self.title("Info: {}".format(entry.getName()))
            self.minsize(300, 100)
            self.focus_get()

            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(1, weight=1)

            tk.Label(self, text="TYPE:").grid(row=0, column=0)
            tk.Label(self, text=ntutils.type_constant_to_str(entry.getType())).grid(row=0, column=1)

            tk.Label(self, text="DATA:").grid(row=1, column=0)
            data = tk.Text(self, height=self.DATA_HEIGHT, width=self.DATA_WIDTH)
            data.insert(tk.END, str(entry.value))
            data.configure(state=tk.DISABLED)
            data.grid(row=1, column=1, sticky=tk.NSEW)

    def __init__(self, master, root_table, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root_table = root_table
        self.hierarchy = deque((root_table,))
        self._last_table_idx = None
        self._items = []
        self._curr_indices = None

        self.scrollbar = tk.Scrollbar(self, command=self._merged_yview)
        self.key_label = tk.Label(self, text="KEY")
        self.key_listbox = tk.Listbox(self, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.value_label = tk.Label(self, text="VALUE")
        self.value_listbox = tk.Listbox(self, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)

        self.lower_frame = tk.Frame(self)
        self.insert_label = tk.Label(self.lower_frame, text="INSERT:")
        self.insert_entry = tk.Entry(self.lower_frame, state=tk.DISABLED)
        self.insert_button = tk.Button(self.lower_frame, command=self._insert_callback, text="Enter")
        self.reload_button = tk.Button(self.lower_frame, command=self._reload_entries(), text="Reload")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.lower_frame.grid_columnconfigure(1, weight=1)

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

        self.key_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.value_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.key_listbox.bind("<Double-Button-1>", self._key_double_click_callback)
        self.value_listbox.bind("<Double-Button-1>", self._value_double_click_callback)
        self.key_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        self.value_listbox.bind("<<ListboxSelect>>", self._listbox_select_callback)
        self.insert_entry.bind("<Return>", self._insert_callback)

        self._populate(self.root_table)

    def _reload_entries(self):
        self._populate(self.hierarchy[-1])

    def _merged_yview(self, *args):
        self.key_listbox.yview(*args)
        self.value_listbox.yview(*args)

    def _wheel_scroll(self, event):
        # TODO: Scrolling can get out of sync for some reason...
        val = -1 * int(event.delta * self.SCROLL_SCALE)
        self.key_listbox.yview_scroll(val, tk.UNITS)
        self.value_listbox.yview_scroll(val, tk.UNITS)

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
            self.EntryPopup(self, self._items[idx])

    def _value_double_click_callback(self, _):
        if len(self._curr_indices) != 1:
            return  # TODO: Some sort of warning or error
        idx = self._curr_indices[0]
        if idx <= self._last_table_idx:
            return  # TODO: Some sort of warning or error
        self.EntryPopup(self, self._items[idx])

    def _populate(self, table):
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
            self._reload_entries()
        except ValueError as e:
            # TODO: This could use some prettification
            Popup(self, "Error: {}".format(str(e)), "Error")

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

    def __init__(self, master, table, width=5, height=5, *args, **kwargs):
        super().__init__(master, width, height, table, *args, **kwargs)
        self.bind_drag_on(self.key_listbox)
        self.bind_drag_on(self.value_listbox)
        self.bind_drag_on(self.key_label)
        self.bind_drag_on(self.value_label)
        self.bind_drag_on(self.insert_label)


# TODO: Robot SVG?
# TODO: Motor monitor
# TODO: Generic network tables entry tracker
# TODO: Log output
