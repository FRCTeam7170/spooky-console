
"""
TODO
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

    def __init__(self, master, text="", mutable=True, on_colour="green", off_colour="red",
                 label_style=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_colour = on_colour
        self.off_colour = off_colour

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


class LabelledText(style.Frame):

    def __init__(self, master, title, text="", title_style=None, text_style=None, *args, **kwargs):
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
        return self.text_var.get()

    @text.setter
    def text(self, val):
        self.text_var.set(val)

    @property
    def title(self):
        return self.title_var.get()

    @title.setter
    def title(self, val):
        self.title_var.set(val)


class DockableLabelledText(DockableMixin, LabelledText):

    def __init__(self, master, title, text="", width=1, height=1, *args, **kwargs):
        super().__init__(master, width, height, title, text, *args, **kwargs)
        self.bind_drag_on(self.text_label)
        self.bind_drag_on(self.title_label)


class BankBase(style.Frame):

    def __init__(self, master, widget_cls, ipadx=2, ipady=2, padx=1, pady=1, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.widgets = []
        self.widget_cls = widget_cls
        self.pack_opts = {"ipadx": ipadx, "ipady": ipady, "padx": padx, "pady": pady}

    def add(self, *args, **kwargs):
        widget = self.widget_cls(self, *args, **kwargs)
        self.widgets.append(widget)
        widget.pack(fill=tk.BOTH, expand=True, **self.pack_opts)
        return widget

    def remove(self, widget):
        widget.destroy()
        self.widgets.remove(widget)


class BooleanIndicatorBank(BankBase):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, BooleanIndicator, *args, **kwargs)


class DockableBooleanIndicatorBank(DockableMixin, BooleanIndicatorBank):

    def __init__(self, master, width=2, height=3, *args, **kwargs):
        super().__init__(master, width, height, *args, **kwargs)

    def add(self, *args, **kwargs):
        bi = super().add(*args, **kwargs)
        self.bind_drag_on(bi)
        if bi.label:
            self.bind_drag_on(bi.label)
        return bi


class LabelledTextBank(BankBase):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, LabelledText, *args, **kwargs)

    def add(self, *args, **kwargs):
        lt = super().add(*args, **kwargs)
        lt.title_label.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        lt.text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return lt


class DockableLabelledTextBank(DockableMixin, LabelledTextBank):

    def __init__(self, master, width=2, height=3, *args, **kwargs):
        super().__init__(master, width, height, *args, **kwargs)

    def add(self, *args, **kwargs):
        lt = super().add(*args, **kwargs)
        self.bind_drag_on(lt)
        self.bind_drag_on(lt.title_label)
        self.bind_drag_on(lt.text_label)
        return lt


class Gyro(style.Canvas):

    # TODO: add label with degrees
    # TODO: style options for canvas items

    def __init__(self, master, radius=100, pointer_frac=3/4, circ_pad=5, auto_resize=True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.circle = self.create_circle(0, 0, 0, width=2)
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


class NTBrowser(style.Frame):

    PARENT_DIR = ".."
    TABLE_FORMAT = "[T] {}"
    ENTRY_FORMAT = "[E] {}"
    BLANK = "-"
    INFO_DATA_WIDTH = 20
    INFO_DATA_HEIGHT = 5

    def __init__(self, master, root_table,
                 scrollbar_style=None,
                 listbox_style=None,
                 header_style=None,
                 label_style=None,
                 entry_style=None,
                 button_style=None,
                 info_text_style=None,
                 *args, **kwargs):
        def_style = kwargs.get("style")
        scrollbar_style = scrollbar_style or def_style
        listbox_style = listbox_style or def_style
        header_style = header_style or def_style
        label_style = label_style or def_style
        entry_style = entry_style or def_style
        button_style = button_style or def_style
        super().__init__(master, *args, **kwargs)
        self.root_table = root_table
        self.hierarchy = deque((root_table,))
        self._last_table_idx = None
        self._items = []
        self._curr_indices = None
        self._curr_scroll_row = 0
        self._entry_popup = popup.PopupManager(self, title_fmt="Info: {}", style=def_style, resizeable=(True, True))
        self._header_style = header_style
        self._label_style = label_style
        self._button_style = button_style
        self._info_text_style = info_text_style or def_style

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

    def __init__(self, master, table, width=5, height=5, *args, **kwargs):
        super().__init__(master, width, height, table, *args, **kwargs)
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
