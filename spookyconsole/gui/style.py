
import tkinter as tk
from tkinter import font as tkfont
from contextlib import contextmanager
from collections import deque


GRAY_SCALE_0 = "#000000"
GRAY_SCALE_1 = "#111111"
GRAY_SCALE_2 = "#222222"
GRAY_SCALE_3 = "#333333"
GRAY_SCALE_4 = "#444444"
GRAY_SCALE_5 = "#555555"
GRAY_SCALE_6 = "#666666"
GRAY_SCALE_7 = "#777777"
GRAY_SCALE_8 = "#888888"
GRAY_SCALE_9 = "#999999"
GRAY_SCALE_A = "#AAAAAA"
GRAY_SCALE_B = "#BBBBBB"
GRAY_SCALE_C = "#CCCCCC"
GRAY_SCALE_D = "#DDDDDD"
GRAY_SCALE_E = "#EEEEEE"
GRAY_SCALE_F = "#FFFFFF"

MUTE_BLUE = "#333355"
MUTE_GREEN = "#335533"
MUTE_RED = "#663333"
MUTE_YELLOW = "#888833"
MUTE_TURQUOISE = "#335555"
MUTE_PURPLE = "#553377"
MUTE_PINK = "#663366"
MUTE_ORANGE = "#774433"

RED_TEAM = "#992222"
BLUE_TEAM = "#222299"
UNKNOWN_TEAM = GRAY_SCALE_B

BOOL_TRUE = MUTE_GREEN
BOOL_FALSE = MUTE_RED

FONT_FAMILY_MONOSPACED = "Courier"
FONT_FAMILY_REGULAR = "Arial"


_tkButton = tk.Button
_tkCanvas = tk.Canvas
_tkCheckbutton = tk.Checkbutton
_tkEntry = tk.Entry
_tkFrame = tk.Frame
_tkLabel = tk.Label
_tkLabelFrame = tk.LabelFrame
_tkListbox = tk.Listbox
_tkMenu = tk.Menu
_tkPanedWindow = tk.PanedWindow
_tkRadiobutton = tk.Radiobutton
_tkScale = tk.Scale
_tkScrollbar = tk.Scrollbar
_tkSpinbox = tk.Spinbox
_tkText = tk.Text
_tkToplevel = tk.Toplevel


_style = deque()
_patched = False


class StyledMixin:

    STYLED_OPTS = []

    def __init__(self, *args, **kwargs):
        if _style:
            kwargs = self._apply_style_to_dict(kwargs)
        super().__init__(*args, **kwargs)

    def restyle(self, **overrides):
        self.configure(**self._apply_style_to_dict(overrides))

    def _apply_style_to_dict(self, conf):
        style = _style[-1]
        for opt in self.STYLED_OPTS:
            if opt in style and opt not in conf:
                conf[opt] = style[opt]
        return conf


class StyledButton(StyledMixin, tk.Button):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify"]


class StyledCanvas(StyledMixin, tk.Canvas):
    STYLED_OPTS = ["bg", "bd", "selectbackground", "selectborderwidth", "selectforeground", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief"]


class StyledCheckbutton(StyledMixin, tk.Checkbutton):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class StyledEntry(StyledMixin, tk.Entry):
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground"]


class StyledFrame(StyledMixin, tk.Frame):
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class StyledLabel(StyledMixin, tk.Label):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify"]


class StyledLabelFrame(StyledMixin, tk.LabelFrame):
    STYLED_OPTS = ["font", "bg", "fg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief",
                   "labelanchor"]


class StyledListbox(StyledMixin, tk.Listbox):
    STYLED_OPTS = ["font", "bg", "activestyle", "fg", "disabledforeground", "bd", "relief", "highlightcolor",
                   "highlightbackground", "highlightthickness", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class StyledMenu(StyledMixin, tk.Menu):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "selectcolor", "relief", "activeborderwidth"]


class StyledPanedWindow(StyledMixin, tk.PanedWindow):
    STYLED_OPTS = ["bg", "bd", "relief", "sashrelief", "showhandle"]


class StyledRadiobutton(StyledMixin, tk.Radiobutton):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class StyledScale(StyledMixin, tk.Scale):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "bd", "showvalue", "sliderrelief", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class StyledScrollbar(StyledMixin, tk.Scrollbar):
    STYLED_OPTS = ["bg", "activebackground", "activerelief", "bd", "elementborderwidth", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class StyledSpinbox(StyledMixin, tk.Spinbox):
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground", "buttonbackground",
                   "buttondownrelief", "buttonuprelief", "insertbackground", "insertborderwidth"]


class StyledText(StyledMixin, tk.Text):
    STYLED_OPTS = ["font", "bg", "fg", "bd", "insertbackground", "insertborderwidth", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class StyledToplevel(StyledMixin, tk.Toplevel):
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


@contextmanager
def stylize(root,
            font_family=None,
            font_size=None,
            font_italic=None,
            font_bold=None,
            font_underline=None,
            font_overstrike=None,
            bg=None,
            active_bg=None,
            fg=None,
            active_fg=None,
            disabled_fg=None,
            bd_width=None,
            highlight_active_colour=None,
            highlight_inactive_colour=None,
            highlight_thickness=None,
            relief=None,
            justify=None,
            **kwargs):
    def add_style(d, key, val):
        if val is not None:
            d[key] = val
        elif key in d:
            del d[key]

    global _style
    new_style = _style[-1].copy() if _style else {}

    font_spec = new_style["font"].actual() if "font" in new_style else {}
    add_style(font_spec, "family", font_family)
    add_style(font_spec, "size", font_size)
    add_style(font_spec, "underline", font_underline)
    add_style(font_spec, "overstrike", font_overstrike)
    add_style(font_spec, "slant", None if font_italic is None else (tkfont.ROMAN, tkfont.ITALIC)[font_italic])
    add_style(font_spec, "weight", None if font_bold is None else (tkfont.NORMAL, tkfont.BOLD)[font_bold])
    new_style["font"] = tkfont.Font(root, **font_spec)

    add_style(new_style, "bg", bg)
    add_style(new_style, "activebackground", active_bg)
    add_style(new_style, "fg", fg)
    add_style(new_style, "activeforeground", active_fg)
    add_style(new_style, "disabledforeground", disabled_fg)
    add_style(new_style, "bd", bd_width)
    add_style(new_style, "highlightcolor", highlight_active_colour)
    add_style(new_style, "highlightbackground", highlight_inactive_colour)
    add_style(new_style, "highlightthickness", highlight_thickness)
    add_style(new_style, "relief", relief)
    add_style(new_style, "justify", justify)
    for k, v in kwargs.items():
        add_style(new_style, k, v)

    patch_changed = False
    try:
        if not _patched:
            patch_changed = True
            patch_tk_widgets()
        _style.append(new_style)
        yield new_style
    finally:
        if patch_changed:
            unpatch_tk_widgets()
        _style.pop()


def patch_tk_widgets():
    global _patched
    _patched = True
    tk.Button = StyledButton
    tk.Canvas = StyledCanvas
    tk.Checkbutton = StyledCheckbutton
    tk.Entry = StyledEntry
    tk.Frame = StyledFrame
    tk.Label = StyledLabel
    tk.LabelFrame = StyledLabelFrame
    tk.Listbox = StyledListbox
    tk.Menu = StyledMenu
    tk.PanedWindow = StyledPanedWindow
    tk.Radiobutton = StyledRadiobutton
    tk.Scale = StyledScale
    tk.Scrollbar = StyledScrollbar
    tk.Spinbox = StyledSpinbox
    tk.Text = StyledText
    tk.Toplevel = StyledToplevel


def unpatch_tk_widgets():
    global _patched
    _patched = False
    tk.Button = _tkButton
    tk.Canvas = _tkCanvas
    tk.Checkbutton = _tkCheckbutton
    tk.Entry = _tkEntry
    tk.Frame = _tkFrame
    tk.Label = _tkLabel
    tk.LabelFrame = _tkLabelFrame
    tk.Listbox = _tkListbox
    tk.Menu = _tkMenu
    tk.PanedWindow = _tkPanedWindow
    tk.Radiobutton = _tkRadiobutton
    tk.Scale = _tkScale
    tk.Scrollbar = _tkScrollbar
    tk.Spinbox = _tkSpinbox
    tk.Text = _tkText
    tk.Toplevel = _tkToplevel
