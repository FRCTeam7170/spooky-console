
"""
TODO
"""

import tkinter as tk
import math
from .core import DockableMixin


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


# TODO: UNIVERSAL STYLING
# TODO: Robot SVG?
# TODO: Motor monitor
# TODO: NETWORK TABLES VIEWER
# TODO: Generic network tables entry tracker
# TODO: Log output
