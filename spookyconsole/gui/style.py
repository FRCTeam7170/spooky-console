
"""
Contains styling utilities for tkinter widgets.

Some features include:

 - a hierarchical styling system for the non-ttk widgets;
 - a collection of colour constants;
 - and reasonable cross-platform named fonts.

"""

import tkinter as tk
import tkinter.font as tkfont
from contextlib import contextmanager


# Colour constants:

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


# Named fonts:

FONT_MONOSPACE_TITLE = None
"""
Tkinter named font with these properties:

 - size: 10
 - family: "Courier"
 - weight: BOLD

``init_fonts`` must be called to initialize this font.
"""

FONT_MONOSPACE_NORMAL = None
"""
Tkinter named font with these properties:

 - size: 8
 - family: "Courier"

``init_fonts`` must be called to initialize this font.
"""

FONT_SERIF_TITLE = None
"""
Tkinter named font with these properties:

 - size: 10
 - family: "Times"
 - weight: BOLD

``init_fonts`` must be called to initialize this font.
"""

FONT_SERIF_NORMAL = None
"""
Tkinter named font with these properties:

 - size: 8
 - family: "Times"

``init_fonts`` must be called to initialize this font.
"""

FONT_SANS_SERIF_TITLE = None
"""
Tkinter named font with these properties:

 - size: 10
 - family: "Helvetica"
 - weight: BOLD

``init_fonts`` must be called to initialize this font.
"""

FONT_SANS_SERIF_NORMAL = None
"""
Tkinter named font with these properties:

 - size: 8
 - family: "Helvetica"

``init_fonts`` must be called to initialize this font.
"""


# Backup copies of "normal" tkinter widgets:

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
"""A global ``Style`` object used by the ``stylize`` context manager."""


class StyleableMixin:
    """
    Mixin class used to make a widget "styleable". This class works in cooperation with the ``Style`` class. Styleable
    widgets should never use their ``widget.configure`` method to set styles in their ``StyleableMixin.STYLED_OPTS``;
    ``StyleableMixin.apply_style`` should be used instead. (Although configuring "functional" styles through
    ``widget.configure`` is perfect fine.)

    There are four sources of style options and they work on a priority system (higher number means higher priority):

        1. ``StyleableMixin.TK_DEFAULT_STYLES``
        2. ``StyleableMixin.DEFAULT_STYLES``
        3. A given ``Style`` instance
        4. A given dictionary of overrides

    """

    STYLED_OPTS = []
    """
    A list of strings specifying all the widget options (i.e. the ones that would normally be passed to
    ``widget.configure(...)``) to be considered for styling; any other options encountered are considered "functional"
    and hence won't be regulated in any way by this class. Subclasses should define this.
    """

    TK_DEFAULT_STYLES = None
    """
    A dictionary of default (platform-specific) styles to revert to if an initially explicitly given style option is
    revoked. This dictionary is lazily built for each unique styled class (i.e. a style is added to this dictionary the
    first time it changes from its default).
    """

    DEFAULT_STYLES = None
    """
    A dictionary of default user-defined styles for a given class. Subclasses may define this. One may also set this at
    runtime through ``StyleableMixin.set_defaults``, but any changes made won't be taken into effect on instances of
    that class until ``StyleableMixin.update_style`` is called.
    """

    def __init__(self, master=None, cnf={}, *args, style=None, **overrides):
        """
        :param master: The master tkinter widget.
        :param cnf: A dictionary of configuration options. This is here to mimic the tkinter widget constructors.
        :type cnf: dict
        :param args: Additional args for the widget constructor.
        :param style: An initial style to employ.
        :type style: Style
        :param overrides: Style overrides to use.
        """
        super().__init__(master, cnf, *args)

        self._style = None
        """The widget's current ``Style``."""

        self._overrides = None
        """A dictionary of the widget's currently-overridden styles."""

        self._assure_default_dicts_exist()
        # Initialize the widget's style to the given style or the global style, which may be set by the stylize context
        # manger.
        self.apply_style(style or _global_style, **overrides)

    def apply_style(self, style=None, *, keep_style=False, keep_overrides=False, **overrides):
        """
        Apply the given style with the given overrides.

        :param style: The style to employ, or None to clear the current style (if ``keep_style`` is False).
        :type style: Style
        :param keep_style: If ``style`` is None, setting this will keep the previous style. Does nothing if ``style`` is
        given.
        :type keep_style: bool
        :param keep_overrides: Whether to append the given ``overrides`` to the already existing overridden styles, or
        replace them.
        :type keep_overrides: bool
        :param overrides: Style overrides to use.
        """
        # Sort out the functional options from the styled ones.
        functional, styled = {}, {}
        for k, v in overrides.items():
            if k in self.STYLED_OPTS:
                styled[k] = v
            else:
                functional[k] = v
        # Directly apply the functional options
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
        """Update this widget's styles."""
        # Alias TK_DEFAULT_STYLES for conciseness.
        tk_defaults = self.__class__.TK_DEFAULT_STYLES
        # Start off the styles_dict with a copy of the tk_defaults, since those styles are of lowest priority (1). We
        # will update the dict with increasing style priority so that lower priority styles will get overridden.
        styles_dict = tk_defaults.copy()
        # Update the dict with the class-specific user-provided defaults. (Priority 2)
        styles_dict.update(self.__class__.DEFAULT_STYLES)
        if self._style:
            # Update the dict with the styles from the Style object. (Priority 3)
            styles_dict.update(self._style.get_relevant_styles(self))
        # Update the dict with the overridden styles. (Priority 4)
        styles_dict.update(self._overrides)
        # Before we actually configure the widget, save any of the styles set to this widget by default so we may return
        # to them if an explicit style option on this widget is removed.
        tk_defaults.update((k, self.cget(k)) for k in styles_dict if k not in tk_defaults)
        self.configure(styles_dict)

    @classmethod
    def _assure_default_dicts_exist(cls):
        """
        Make sure that this class's ``StyleableMixin.TK_DEFAULT_STYLES`` and ``StyleableMixin.DEFAULT_STYLES`` are
        defined (every class needs its own version of these; if they were initialized to an empty dict in
        ``StyleableMixin`` then all classes would share the same dictionaries).
        """
        if cls.TK_DEFAULT_STYLES is None:
            cls.TK_DEFAULT_STYLES = {}
        if cls.DEFAULT_STYLES is None:
            cls.DEFAULT_STYLES = {}

    @classmethod
    def set_defaults(cls, keep_existing=True, **defaults):
        """
        Convenience method to update the default styles for this class.

        :param keep_existing: Whether to keep the already existing default styles, or replace them.
        :type keep_existing: bool
        :param defaults: A dictionary of default styles.
        """
        cls._assure_default_dicts_exist()
        if keep_existing:
            cls.DEFAULTS.update(defaults)
        else:
            cls.DEFAULTS = defaults


# TODO: Styleable Tk (root)?


class Button(StyleableMixin, tk.Button):
    """Styleable version of ``tkinter.Button``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify"]


class Canvas(StyleableMixin, tk.Canvas):
    """Styleable version of ``tkinter.Canvas``."""
    STYLED_OPTS = ["bg", "bd", "selectbackground", "selectborderwidth", "selectforeground", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief"]


class Checkbutton(StyleableMixin, tk.Checkbutton):
    """Styleable version of ``tkinter.Checkbutton``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class Entry(StyleableMixin, tk.Entry):
    """Styleable version of ``tkinter.Entry``."""
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground"]


class Frame(StyleableMixin, tk.Frame):
    """Styleable version of ``tkinter.Frame``."""
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Label(StyleableMixin, tk.Label):
    """Styleable version of ``tkinter.Label``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify"]


class LabelFrame(StyleableMixin, tk.LabelFrame):
    """Styleable version of ``tkinter.LabelFrame``."""
    STYLED_OPTS = ["font", "bg", "fg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief",
                   "labelanchor"]


class Listbox(StyleableMixin, tk.Listbox):
    """Styleable version of ``tkinter.Listbox``."""
    STYLED_OPTS = ["font", "bg", "activestyle", "fg", "disabledforeground", "bd", "relief", "highlightcolor",
                   "highlightbackground", "highlightthickness", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class Menu(StyleableMixin, tk.Menu):
    """Styleable version of ``tkinter.Menu``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "selectcolor", "relief", "activeborderwidth"]


class PanedWindow(StyleableMixin, tk.PanedWindow):
    """Styleable version of ``tkinter.PanedWindow``."""
    STYLED_OPTS = ["bg", "bd", "relief", "sashrelief", "showhandle"]


class Radiobutton(StyleableMixin, tk.Radiobutton):
    """Styleable version of ``tkinter.Radiobutton``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "activeforeground", "disabledforeground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "overrelief", "justify",
                   "indicatoron", "offrelief", "selectcolor"]


class Scale(StyleableMixin, tk.Scale):
    """Styleable version of ``tkinter.Scale``."""
    STYLED_OPTS = ["font", "bg", "activebackground", "fg", "bd", "showvalue", "sliderrelief", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Scrollbar(StyleableMixin, tk.Scrollbar):
    """Styleable version of ``tkinter.Scrollbar``."""
    STYLED_OPTS = ["bg", "activebackground", "activerelief", "bd", "elementborderwidth", "troughcolor",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Spinbox(StyleableMixin, tk.Spinbox):
    """Styleable version of ``tkinter.Spinbox``."""
    STYLED_OPTS = ["font", "bg", "disabledbackground", "fg", "disabledforeground", "readonlybackground", "bd",
                   "highlightcolor", "highlightbackground", "highlightthickness", "relief", "justify",
                   "selectbackground", "selectborderwidth", "selectforeground", "buttonbackground",
                   "buttondownrelief", "buttonuprelief", "insertbackground", "insertborderwidth"]


class Text(StyleableMixin, tk.Text):
    """Styleable version of ``tkinter.Text``."""
    STYLED_OPTS = ["font", "bg", "fg", "bd", "insertbackground", "insertborderwidth", "highlightcolor",
                   "highlightbackground", "highlightthickness", "relief", "selectbackground", "selectborderwidth",
                   "selectforeground"]


class Toplevel(StyleableMixin, tk.Toplevel):
    """Styleable version of ``tkinter.Toplevel``."""
    STYLED_OPTS = ["bg", "bd", "highlightcolor", "highlightbackground", "highlightthickness", "relief"]


class Style:
    """
    A dictionary proxy for tkinter widget styles. ``StyleableMixin``s register themselves to ``Style``s so that whenever
    a ``Style`` is updated, any registered ``StyleableMixin``s are automatically updated to reflect the changes.

    ``Style``s employ a parent-child system in which a ``Style`` can have one or more parents to inherit styles from.
    When a style is requested from a ``Style`` and cannot be found in said ``Style``'s own styles, the style is looked
    for in its ancestors, prioritizing the first ones specified in the constructor. When a ``Style`` is updated, all
    child ``Style``s of the changed ``Style`` are recursively informed of the change.
    """

    DEFAULTS = {}
    """Global default styles for all ``Style`` objects. This should be set through ``Style.set_defaults``."""

    def __init__(self, *parents, **styles):
        """
        :param parents: ``Style``s to inherit styles from.
        :param styles: Styles to use.
        """
        self._dict = styles
        """A dictionary of the styles specific to this ``Style``."""

        self._styled = []
        """
        A list of registered ``StyleableMixin``s. These are signaled of any changes to this ``Style`` in
        ``Style._signal_style_changed``.
        """

        self._parents = parents
        """A list of this ``Style``'s parent ``Style``s."""

        self._children = []
        """
        A list of registered child ``Style``s. These are signaled of any changes to this ``Style`` in
        ``Style._signal_style_changed``.
        """

        for parent in parents:
            parent._register_child(self)

    def register_styleable(self, styleable):
        """
        Called by ``StyleableMixin`` objects to receive updates on whenever this style changes. This should not be
        called by user code.

        :param styleable: The styleable widget to register.
        :type styleable: StyleableMixin
        """
        self._styled.append(styleable)

    def unregister_styleable(self, styleable):
        """
        Called by ``StyleableMixin`` objects to stop receiving updates on whenever this style changes. This should not
        be called by user code.

        :param styleable: The styleable widget to unregister.
        :type styleable: StyleableMixin
        """
        # This will raise an error if the styleable is not already registered.
        self._styled.remove(styleable)

    def _register_child(self, style):
        """
        Called by child ``Style``s to receive updates on whenever this style changes.

        :param style: The child ``Style``.
        :type style: Style
        """
        self._children.append(style)

    # Keep the same naming scheme as tkinter.
    def configure(self, **kwargs):
        """
        Configure this ``Style``'s styles.

        :param kwargs: The styles to add/edit.
        """
        self._dict.update(kwargs)
        self._signal_style_changed()

    config = configure
    """Alias for ``Style.configure``."""

    def remove_styles(self, *styles):
        """
        Remove the given styles from this ``Style``. This will raise a ``KeyError`` if any of the given style names are
        not in this ``Style``.

        :param styles: Style names to remove.
        """
        for style in styles:
            del self._dict[style]
        self._signal_style_changed()

    def _signal_style_changed(self):
        """
        Internal method to update all the ``StyleableMixin`` widgets registered to this ``Style`` and its children.
        """
        for s in self._styled:
            s.update_style()
        for child in self._children:
            child._signal_style_changed()

    def get_relevant_styles(self, widget):
        """
        Determine and return all the styles in this ``Style`` recognized by the given tkinter widget.

        :param widget: The tkinter widget to find styles for.
        :return: All the styles recognized by the given tkinter widget.
        """
        return {k: v for k, v in map(lambda k: (k, self.get_style(k)), widget.keys()) if v is not None}

    def get_style(self, key):
        """
        Return the style corresponding to the given style name, first checking this ``Style`` and its parents, then
        resorting to the global default styles (``Style.DEFAULTS``).

        :param key: The style name.
        :type key: str
        :return: The style corresponding to the given style name or None if it could not be found.
        """
        return self._get_style(key) or self.__class__.DEFAULTS.get(key)

    def _get_style(self, key):
        """
        Attempt to retrieve the given style from this ``Style``'s ``Style._dict``. If that fails, recursively search
        this widget's parents.

        :param key: The style name.
        :type key: str
        :return: The style corresponding to the given style name or None if it could not be found.
        """
        ret = self._dict.get(key)
        if ret is None:
            for p in self._parents:
                ret = p._get_style(key)
                if ret is not None:
                    break
        return ret

    @classmethod
    def set_defaults(cls, keep_existing=True, **defaults):
        """
        Convenience method to update the global default styles (``Style.DEFAULTS``).

        :param keep_existing: Whether to keep the already existing default styles, or replace them.
        :type keep_existing: bool
        :param defaults: A dictionary of styles.
        """
        if keep_existing:
            cls.DEFAULTS.update(defaults)
        else:
            cls.DEFAULTS = defaults


def patch_tk_widgets():
    """Monkey patch the tkinter widgets with their styleable equivalents."""
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
    """Revert the tkinter widgets back to their defaults after monkey patching them with ``patch_tk_widgets``."""
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
    """Context manager to temporarily monkey patch the tkinter widgets with their styleable equivalents."""
    try:
        patch_tk_widgets()
        yield
    finally:
        unpatch_tk_widgets()


@contextmanager
def stylize(style, **overrides):
    """
    Context manager to temporarily apply a global-level style and some overrides. This global-level style will only be
    used by ``StyleableMixin``s if they're not explicitly given a ``Style`` object already.

    :param style: The style to apply.
    :type style: Style
    :param overrides: Style overrides to use.
    """
    global _global_style
    try:
        _global_style = Style(style, **overrides) if overrides else style
        yield
    finally:
        _global_style = None


def init_fonts(root):
    """
    Initialize all the named fonts. This must be called prior to attempting to use any of the named fonts.

    :param root: The tkinter root widget.
    :type root: tkinter.Tk
    """
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
                                   family="Times",
                                   weight=tkfont.BOLD)

    FONT_SERIF_NORMAL = tkfont.Font(root, size=8,
                                    name="FONT_SERIF_NORMAL",
                                    family="Times")

    FONT_SANS_SERIF_TITLE = tkfont.Font(root, size=10,
                                        name="FONT_SANS_SERIF_TITLE",
                                        family="Helvetica",
                                        weight=tkfont.BOLD)

    FONT_SANS_SERIF_NORMAL = tkfont.Font(root, size=8,
                                         name="FONT_SANS_SERIF_NORMAL",
                                         family="Helvetica")
