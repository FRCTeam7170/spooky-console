
import tkinter as tk
from tkinter import font as tkfont
from contextlib import contextmanager


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


class StyledMixin:

    STYLED_OPTS = []

    def __init__(self, *args, **kwargs):
        print(type(self))
        for opt in self.STYLED_OPTS:
            if opt in GLOBAL_STYLE:
                if opt == "troughcolor":
                    print("TC")
                self._apply(kwargs, opt, GLOBAL_STYLE[opt])
        super().__init__(*args, **kwargs)

    @staticmethod
    def _apply(kwargs, key, value):
        if key not in kwargs:
            kwargs[key] = value


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


GLOBAL_STYLE = {}


@contextmanager
def stylize(root,
            font_family=FONT_FAMILY_MONOSPACED,
            font_size=11,
            font_italic=False,
            font_bold=False,
            font_underline=False,
            font_overstrike=False,
            bg=GRAY_SCALE_4,
            active_bg=GRAY_SCALE_2,
            fg=GRAY_SCALE_E,
            active_fg=GRAY_SCALE_5,
            disabled_fg=GRAY_SCALE_5,
            bd_width=1,
            highlight_active_colour=GRAY_SCALE_0,
            highlight_unactive_colour=GRAY_SCALE_0,
            highlight_thickness=0,
            relief=None,
            justify=tk.LEFT,
            **kwargs):
    def add_if_non_none(d, key, val):
        if val is not None:
            d[key] = val

    global GLOBAL_STYLE
    GLOBAL_STYLE = {}

    font_spec = {}
    add_if_non_none(font_spec, "family", font_family)
    add_if_non_none(font_spec, "size", font_size)
    add_if_non_none(font_spec, "underline", font_underline)
    add_if_non_none(font_spec, "overstrike", font_overstrike)
    if font_italic is not None:
        font_spec["slant"] = tkfont.ITALIC if font_italic else tkfont.ROMAN
    if font_bold is not None:
        font_spec["weight"] = tkfont.BOLD if font_bold else tkfont.NORMAL
    GLOBAL_STYLE["font"] = tkfont.Font(root, **font_spec)

    add_if_non_none(GLOBAL_STYLE, "bg", bg)
    add_if_non_none(GLOBAL_STYLE, "activebackground", active_bg)
    add_if_non_none(GLOBAL_STYLE, "fg", fg)
    add_if_non_none(GLOBAL_STYLE, "activeforeground", active_fg)
    add_if_non_none(GLOBAL_STYLE, "disabledforeground", disabled_fg)
    add_if_non_none(GLOBAL_STYLE, "bd", bd_width)
    add_if_non_none(GLOBAL_STYLE, "highlightcolor", highlight_active_colour)
    add_if_non_none(GLOBAL_STYLE, "highlightbackground", highlight_unactive_colour)
    add_if_non_none(GLOBAL_STYLE, "highlightthickness", highlight_thickness)
    add_if_non_none(GLOBAL_STYLE, "relief", relief)
    add_if_non_none(GLOBAL_STYLE, "justify", justify)
    GLOBAL_STYLE.update(kwargs)

    try:
        patch_tk_widgets()
        yield
    finally:
        unpatch_tk_widgets()


def patch_tk_widgets():
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
