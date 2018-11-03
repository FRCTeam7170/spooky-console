
"""Contains utilities for generating popup windows in tkinter."""

import tkinter as tk
from collections import deque, namedtuple, OrderedDict
from functools import partial
import spookyconsole.gui.style as style


_CurrentPopup = namedtuple("_CurrentPopup", ("widget", "on_close"))


# A function that accepts any arguments and does nothing.
def _null_func(*_, **__):
    pass


class PopupManager(style.Toplevel):
    """
    A ``spookyconsole.gui.style.Toplevel`` widget for creating popup windows. ``PopupManager`` only permits (by
    necessity) having one popup window open per instance at a time. If the user tries to open a popup window (via
    ``PopupManager.create``) while another is already open, that window will be added to a FIFO queue to be displayed
    once the currently-open popup is closed.
    """

    DEFAULT_PACK_OPTS = {"fill": tk.BOTH, "expand": True}
    """The tkinter pack options to use if none are given in ``PopupManager.create``."""

    def __init__(self, master, *args, min_size=(200, 100), resizeable=(False, False), title_fmt="{}", **kwargs):
        """
        :param master: The master tkinter widget.
        :param args: Additional args for the ``spookyconsole.gui.style.Toplevel`` constructor.
        :param min_size: The minimum size of the popup window as a (width, height) 2-tuple.
        :type min_size: tuple
        :param resizeable: Whether the popup window may be resized in either direction as a (width, height) 2-tuple.
        :type resizeable: tuple
        :param title_fmt: The format for each popup's title. Must contain one pair of curly braces to substitute the
        title give in ``PopupManager.create`` into.
        :type title_fmt: str
        :param kwargs: Additional kwargs for the ``spookyconsole.gui.style.Toplevel`` constructor.
        """
        super().__init__(master, *args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close_current_popup)
        self.minsize(*min_size)
        self.resizable(*resizeable)
        # Make the window invisible by default since no popups have been created yet.
        self.withdraw()

        self._title_fmt = title_fmt
        """
        The format of each popup's title. Must contain one pair of curly braces to substitute the title give in
        ``PopupManager.create`` into.
        """

        self._open = None
        """
        Stores information on the currently-open popup as a ``_CurrentPopup`` namedtuple or None if no popup is open.
        """

        self._queue = deque()
        """A FIFO queue of scheduled popups."""

    @property
    def popup_open(self):
        """
        :return: Whether or not a popup window is currently open.
        :rtype: bool
        """
        return bool(self._open)

    def create(self, widget, title, on_open=_null_func, on_close=_null_func, **pack_opts):
        """
        Create a new popup window composed of the given widget. If a popup window is already open, the new popup window
        will be scheduled.

        :param widget: The tkinter widget to pack into the popup window.
        :param title: The title of the popup window. This will be formatted into ``PopupManager._title_fmt``.
        :type title: str
        :param on_open: A callable to be invoked when the popup opens.
        :param on_close: A callable to be invoked when the popup closes.
        :param pack_opts: Kwargs to use as the tkinter pack options for the given widget. Defaults to
        ``PopupManager.DEFAULT_PACK_OPTS``.
        """
        pack_opts = pack_opts or self.DEFAULT_PACK_OPTS
        self._queue.append((widget, title, on_open, on_close, pack_opts))
        if not self._open:
            self._open_next()

    def _open_next(self):
        """Open the next queued popup window."""
        widget, title, on_open, on_close, pack_opts = self._queue.popleft()
        self.title(self._title_fmt.format(title))
        widget.pack(**pack_opts)
        self._open = _CurrentPopup(widget, on_close)
        self.deiconify()  # Show the popup window.
        self.focus_get()
        on_open()

    def close_current_popup(self):
        """Close the currently-open popup window."""
        self.withdraw()  # Make the popup window invisible.
        self._open.widget.destroy()
        self._open.on_close()
        self._open = None
        if self._queue:
            self._open_next()


_GLOBAL_PM = None
"""The ``PopupManager`` to use for popup windows generated from ``dialog``."""

# Some default button configurations.
BUTTONS_OK = OrderedDict((("Ok", True),))
BUTTONS_OK_CANCEL = OrderedDict((("Ok", True), ("Cancel", False)))
BUTTONS_YES_NO = OrderedDict((("Yes", True), ("No", False)))
BUTTONS_YES_NO_CANCEL = OrderedDict((("Yes", True), ("No", False), ("Cancel", None)))


def init_global_pm(root, *args, **kwargs):
    """
    Initialize the global ``PopupManager`` (``_GLOBAL_PM``) used for popup windows generated from ``dialog``.

    :param root: The tkinter root widget.
    :type root: tkinter.Tk
    :param args: Additional args for the ``PopupManager`` constructor.
    :param kwargs: Additional kwargs for the ``PopupManager`` constructor.
    """
    global _GLOBAL_PM
    _GLOBAL_PM = PopupManager(root, *args, **kwargs)


def dialog(title, message, buttons=(), on_open=_null_func, on_close=_null_func,
           frame_style=None, message_style=None, button_style=None):
    """
    Create a popup window using the global ``PopupManager`` (``_GLOBAL_PM``). The ``_GLOBAL_PM`` must be initialized
    before calling ``dialog`` (via ``init_global_pm``) lest a ``RuntimeError`` will be raised.

    The created popup window consists of a simple message and, optionally, some buttons. The buttons are specified as a
    dictionary in which the keys are the button's text (as a string) and the values are arbitrary. When any one of the
    buttons is clicked the popup window will close and ``on_close`` will be called with the clicked button's
    corresponding value from the ``buttons`` dictionary or None if the popup window is exited normally. The message
    appears in the centre of the popup window and the buttons in the bottom-right corner. If it be desired that the
    buttons appear in a specific order, use a ``collections.OrderedDict`` (the first element will be the leftmost
    button).

    :param title: The title of the popup window.
    :type title: str
    :param message: The message to display in the popup window.
    :type title: str
    :param buttons: The buttons to display in the popup window (see above).
    :type title: dict
    :param on_open: A callable to be invoked when the popup opens.
    :param on_close: A callable to be invoked when the popup closes. It will be passed the value in the dictionary
    corresponding to what button was pressed or None if the popup window was exited normally.
    :param frame_style: The style for the frames.
    :type frame_style: spookyconsole.gui.style.Style
    :param message_style: The style for the message label.
    :type message_style: spookyconsole.gui.style.Style
    :param button_style: The style for the buttons.
    :type button_style: spookyconsole.gui.style.Style
    """
    def btn_callback(btn):
        nonlocal ret
        ret = buttons.get(btn)
        _GLOBAL_PM.close_current_popup()

    if not _GLOBAL_PM:
        raise RuntimeError("_GLOBAL_PM not initialized")
    ret = None
    frame = style.Frame(_GLOBAL_PM, style=frame_style)
    # Make only the message resizeable.
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    style.Label(frame, style=message_style, text=message).grid(row=0, column=0)
    btn_frame = style.Frame(frame, style=frame_style)
    for btn_text in buttons:
        btn = style.Button(btn_frame, style=button_style, text=btn_text, command=partial(btn_callback, btn_text))
        # Pack each button to the left so that if a OrderedDict is used, the buttons appear in order.
        btn.pack(side=tk.LEFT, padx=2, pady=2)
    btn_frame.grid(row=1, column=0, sticky=tk.E)
    _GLOBAL_PM.create(frame, title, on_open=on_open, on_close=lambda: on_close(ret))
