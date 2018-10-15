
"""
TODO
"""

import tkinter as tk
from gui.core import DockableMixin, DragPoint


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


# TODO: Gryo
# TODO: Robot SVG?
# TODO: Motor monitor
# TODO: Generic boolean widget
# TODO: Generic toggle button
# TODO: NETWORK TABLES VIEWER
# TODO: Generic network tables entry tracker
# TODO: Log output
