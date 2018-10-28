
import tkinter as tk
import tkinter.font as tkfont
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


FONT_MONOSPACE_TITLE = None
FONT_MONOSPACE_NORMAL = None
FONT_SERIF_TITLE = None
FONT_SERIF_NORMAL = None
FONT_SANS_SERIF_TITLE = None
FONT_SANS_SERIF_NORMAL = None


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


_global_style = None


class StyleableMixin:

    STYLED_OPTS = []
    TK_DEFAULT_STYLES = None
    DEFAULT_STYLES = None

    def __init__(self, master=None, cnf={}, *args, style=None, **overrides):
        super().__init__(master, cnf, *args)
        self._style = None
        self._overrides = None
        self._assure_default_dicts_exist()
        self.apply_style(style or _global_style, **overrides)

    def apply_style(self, style=None, *, keep_style=False, keep_overrides=False, **overrides):
        functional, styled = {}, {}
        for k, v in overrides.items():
            if k in self.STYLED_OPTS:
                styled[k] = v
            else:
                functional[k] = v
        self.configure(functional)
        if keep_overrides:
            self._overrides.update(styled)
        else:
            self._overrides = styled
        if style:
            if self._style:
                self._style.unregister_styleable(self)
            self._style = style
            style.register_styleable(self)
        elif self._style and not keep_style:
            self._style.unregister_styleable(self)
            self._style = None
        self.update_style()

    def update_style(self):
        tk_defaults = self.__class__.TK_DEFAULT_STYLES
        styles_dict = tk_defaults.copy()
        styles_dict.update(self.__class__.DEFAULT_STYLES)
        if self._style:
            styles_dict.update(self._style.get_relevant_styles(self))
        styles_dict.update(self._overrides)
        tk_defaults.update((k, self.cget(k)) for k in styles_dict if k not in tk_defaults)
        self.configure(styles_dict)

    @classmethod
    def _assure_default_dicts_exist(cls):
        if cls.TK_DEFAULT_STYLES is None:
            cls.TK_DEFAULT_STYLES = {}
        if cls.DEFAULT_STYLES is None:
            cls.DEFAULT_STYLES = {}

    @classmethod
    def set_defaults(cls, keep_existing=True, **defaults):
        if keep_existing:
            cls.DEFAULTS.update(defaults)
        else:
            cls.DEFAULTS = defaults


# TODO: Styleable Tk (root)


class Button(StyleableMixin, tk.Button):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify"]


class Canvas(StyleableMixin, tk.Canvas):
    STYLED_OPTS = ["bg", "bd", "selectbackground", "selectborderwidth", "selectforeground", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief"]


class Checkbutton(StyleableMixin, tk.Checkbutton):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class Entry(StyleableMixin, tk.Entry):
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground"]


class Frame(StyleableMixin, tk.Frame):
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Label(StyleableMixin, tk.Label):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify"]


class LabelFrame(StyleableMixin, tk.LabelFrame):
    STYLED_OPTS = ["font", "bg", "fg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief",
                   "labelanchor"]


class Listbox(StyleableMixin, tk.Listbox):
    STYLED_OPTS = ["font", "bg", "activestyle", "fg", "disabledforeground", "bd", "relief", "highlightcolor",
                   "highlightbackground", "highlightthickness", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class Menu(StyleableMixin, tk.Menu):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "selectcolor", "relief", "activeborderwidth"]


class PanedWindow(StyleableMixin, tk.PanedWindow):
    STYLED_OPTS = ["bg", "bd", "relief", "sashrelief", "showhandle"]


class Radiobutton(StyleableMixin, tk.Radiobutton):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class Scale(StyleableMixin, tk.Scale):
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "bd", "showvalue", "sliderrelief", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Scrollbar(StyleableMixin, tk.Scrollbar):
    STYLED_OPTS = ["bg", "activebackground", "activerelief", "bd", "elementborderwidth", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Spinbox(StyleableMixin, tk.Spinbox):
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground", "buttonbackground",
                   "buttondownrelief", "buttonuprelief", "insertbackground", "insertborderwidth"]


class Text(StyleableMixin, tk.Text):
    STYLED_OPTS = ["font", "bg", "fg", "bd", "insertbackground", "insertborderwidth", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class Toplevel(StyleableMixin, tk.Toplevel):
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Style:

    DEFAULTS = {}

    def __init__(self, *parents, **kwargs):
        self._dict = kwargs
        self._styled = []
        self._parents = parents

    def register_styleable(self, styleable):
        self._styled.append(styleable)

    def unregister_styleable(self, styleable):
        self._styled.remove(styleable)

    def configure(self, **kwargs):
        self._dict.update(kwargs)
        self._signal_style_changed()

    config = configure

    def _signal_style_changed(self):
        for s in self._styled:
            s.update_style()

    def get_relevant_styles(self, widget):
        return {k: v for k, v in map(lambda k: (k, self.get_style(k)), widget.keys()) if v is not None}

    def get_style(self, key):
        return self._get_style(key) or self.__class__.DEFAULTS.get(key)

    def _get_style(self, key):
        ret = self._dict.get(key)
        if ret is None:
            for p in self._parents:
                ret = p._get_style(key)
                if ret is not None:
                    break
        return ret

    @classmethod
    def set_defaults(cls, keep_existing=True, **defaults):
        if keep_existing:
            cls.DEFAULTS.update(defaults)
        else:
            cls.DEFAULTS = defaults


def patch_tk_widgets():
    tk.Button = Button
    tk.Canvas = Canvas
    tk.Checkbutton = Checkbutton
    tk.Entry = Entry
    tk.Frame = Frame
    tk.Label = Label
    tk.LabelFrame = LabelFrame
    tk.Listbox = Listbox
    tk.Menu = Menu
    tk.PanedWindow = PanedWindow
    tk.Radiobutton = Radiobutton
    tk.Scale = Scale
    tk.Scrollbar = Scrollbar
    tk.Spinbox = Spinbox
    tk.Text = Text
    tk.Toplevel = Toplevel


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


@contextmanager
def patch():
    try:
        patch_tk_widgets()
        yield
    finally:
        unpatch_tk_widgets()


@contextmanager
def stylize(style, **overrides):
    global _global_style
    try:
        _global_style = Style(style, **overrides) if overrides else style
        yield
    finally:
        _global_style = None


def init_fonts(root):
    global FONT_MONOSPACE_TITLE, FONT_MONOSPACE_NORMAL,\
        FONT_SERIF_TITLE, FONT_SERIF_NORMAL,\
        FONT_SANS_SERIF_TITLE, FONT_SANS_SERIF_NORMAL

    FONT_MONOSPACE_TITLE = tkfont.Font(root, size=10,
                                       name="FONT_MONOSPACE_TITLE",
                                       family="Courier",
                                       weight=tkfont.BOLD)

    FONT_MONOSPACE_NORMAL = tkfont.Font(root, size=8,
                                        name="FONT_MONOSPACE_NORMAL",
                                        family="Courier")

    FONT_SERIF_TITLE = tkfont.Font(root, size=10,
                                   name="FONT_SERIF_TITLE",
                                   family="Helvetica",
                                   weight=tkfont.BOLD)

    FONT_SERIF_NORMAL = tkfont.Font(root, size=8,
                                        name="FONT_SERIF_NORMAL",
                                        family="Helvetica")

    FONT_SANS_SERIF_TITLE = tkfont.Font(root, size=10,
                                        name="FONT_SANS_SERIF_TITLE",
                                        family="Times",
                                        weight=tkfont.BOLD)

    FONT_SANS_SERIF_NORMAL = tkfont.Font(root, size=8,
                                         name="FONT_SANS_SERIF_NORMAL",
                                         family="Times")
