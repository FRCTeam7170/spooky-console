
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


from networktables.instance import NetworkTablesInstance
import random


class TableSim:

    class EntrySim:

        def __init__(self, value, path):
            self.value = value
            self.key = path

        def getName(self):
            return self.key

        def getType(self):
            return random.choice([NetworkTablesInstance.EntryTypes.BOOLEAN,
                                  NetworkTablesInstance.EntryTypes.DOUBLE,
                                  NetworkTablesInstance.EntryTypes.STRING,
                                  NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY,
                                  NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY,
                                  NetworkTablesInstance.EntryTypes.STRING_ARRAY])

    PATH_SEPARATOR = '/'

    def __init__(self, data, path=PATH_SEPARATOR):
        self.data = data
        self.path = path

    def getEntry(self, key):
        ret = self.data[key]
        assert self.is_entry(ret)
        return self.EntrySim(ret, key)

    def getSubTable(self, key):
        ret = self.data[key]
        assert self.is_sub_table(ret)
        return TableSim(ret, self.path + key + self.PATH_SEPARATOR)

    def getKeys(self):
        return [key for key, value in self.data.items() if not isinstance(value, dict)]

    def getSubTables(self):
        return [key for key, value in self.data.items() if isinstance(value, dict)]

    def containsKey(self, key):
        try:
            return not isinstance(self.data[key], dict)
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
        return not isinstance(data, dict)


class NTBrowser(tk.Frame):

    PARENT_DIR = ".."
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
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)

            tk.Label(self, text="TYPE:").grid(row=0, column=0)
            tk.Label(self, text=ntutils.type_constant_to_str(entry.getType())).grid(row=0, column=1)

            # TODO: Make data auto-update?
            tk.Label(self, text="DATA:").grid(row=1, column=0)
            data = tk.Text(self, height=self.DATA_HEIGHT, width=self.DATA_WIDTH)
            data.insert(tk.END, str(entry.value))
            data.configure(state=tk.DISABLED)
            data.grid(row=1, column=1, sticky=tk.NSEW)

    def __init__(self, master, root_table, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root_table = root_table
        self.hierarchy = deque((root_table,))

        self.scrollbar = tk.Scrollbar(self, command=self._merged_yview)
        self.key_listbox = tk.Listbox(self, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.value_listbox = tk.Listbox(self, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.entry = tk.Entry(self)

        self.key_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.key_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.value_listbox.bind("<MouseWheel>", self._wheel_scroll)
        self.key_listbox.bind("<Double-Button-1>", self._key_double_click_callback)
        self.value_listbox.bind("<Double-Button-1>", self._value_double_click_callback)

        self._populate(self.root_table)

    def _merged_yview(self, *args):
        self.key_listbox.yview(*args)
        self.value_listbox.yview(*args)

    def _wheel_scroll(self, event):
        # TODO: Scrolling can get out of sync for some reason...
        val = -1 * int(event.delta * self.SCROLL_SCALE)
        self.key_listbox.yview_scroll(val, tk.UNITS)
        self.value_listbox.yview_scroll(val, tk.UNITS)

    def _key_double_click_callback(self, _):
        selected = self.key_listbox.curselection()
        if len(selected) != 1:
            return  # TODO: Some sort of warning or error
        selected = self.key_listbox.get(selected[0])
        if selected == self.PARENT_DIR:
            self.hierarchy.pop()
            assert len(self.hierarchy)  # TODO: TEMP
            self._populate(self.hierarchy[-1])
        elif self.hierarchy[-1].containsSubTable(selected):
            table = self.hierarchy[-1].getSubTable(selected)
            self.hierarchy.append(table)
            self._populate(table)
        else:  # self.hierarchy[-1].containsKey(selected)
            pass  # TODO

    def _value_double_click_callback(self, _):
        # TODO: This is mostly dupe code...
        selected = self.value_listbox.curselection()
        if len(selected) != 1:
            return  # TODO: Some sort of warning or error
        if self.value_listbox.get(selected[0]) == "-":  # TODO: TEMP, need prettier blank/placeholder
            return
        selected = self.key_listbox.get(selected[0])
        self.EntryPopup(self, self.hierarchy[-1].getEntry(selected))

    def _populate(self, table):
        # TODO: Add indicator like "[T]" or "[E]" to keys
        self._clear()
        if table is not self.root_table:
            self._append_pair(self.PARENT_DIR, "-")
        for subtable in table.getSubTables():
            self._append_pair(subtable, "-")
        for key in table.getKeys():
            self._append_pair(key, table.getEntry(key).value)

    def _append_pair(self, key, value):
        self.key_listbox.insert(tk.END, key)
        self.value_listbox.insert(tk.END, value)

    def _clear(self):
        self.key_listbox.delete(0, tk.END)
        self.value_listbox.delete(0, tk.END)


class DockableNTBrowser(DockableMixin, NTBrowser):
    pass


# TODO: UNIVERSAL STYLING
# TODO: Robot SVG?
# TODO: Motor monitor
# TODO: Generic network tables entry tracker
# TODO: Log output
