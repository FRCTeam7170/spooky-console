
import tkinter as tk
from collections import deque, namedtuple
from functools import partial
import spookyconsole.gui.style as style


_CurrentPopup = namedtuple("_CurrentPopup", ("widget", "on_close"))


def _null_func(*_, **__):
    pass


class PopupManager(style.Toplevel):

    DEFAULT_PACK_OPTS = {"fill": tk.BOTH, "expand": True}

    def __init__(self, master, *args, min_size=(200, 100), resizeable=(False, False), title_fmt="{}", **kwargs):
        super().__init__(master, *args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close_current_popup)
        self.minsize(*min_size)
        self.resizable(*resizeable)
        self.withdraw()
        self._title_fmt = title_fmt
        self._open = None
        self._queue = deque()

    @property
    def popup_open(self):
        return bool(self._open)

    def create(self, widget, title, on_open=_null_func, on_close=_null_func, **pack_opts):
        pack_opts = pack_opts or self.DEFAULT_PACK_OPTS
        self._queue.append((widget, title, on_open, on_close, pack_opts))
        if not self._open:
            self._open_next()

    def _open_next(self):
        widget, title, on_open, on_close, pack_opts = self._queue.popleft()
        self.title(self._title_fmt.format(title))
        widget.pack(**pack_opts)
        self._open = _CurrentPopup(widget, on_close)
        self.deiconify()
        self.focus_get()
        on_open()

    def close_current_popup(self):
        self.withdraw()
        self._open.widget.destroy()
        self._open.on_close()
        self._open = None
        if self._queue:
            self._open_next()


_GLOBAL_PM = None
BUTTONS_OK = {"Ok": True}
BUTTONS_OK_CANCEL = {"Ok": True, "Cancel": False}
BUTTONS_YES_NO = {"Yes": True, "No": False}
BUTTONS_YES_NO_CANCEL = {"Yes": True, "No": False, "Cancel": None}


def init_global_pm(root, *args, **kwargs):
    global _GLOBAL_PM
    _GLOBAL_PM = PopupManager(root, *args, **kwargs)


def dialog(title, message, buttons=(), on_open=_null_func, on_close=_null_func,
           frame_style=None, message_style=None, button_style=None):
    def btn_callback(btn):
        nonlocal ret
        ret = buttons.get(btn)
        _GLOBAL_PM.close_current_popup()

    if not _GLOBAL_PM:
        raise RuntimeError("_GLOBAL_PM not initialized")
    ret = None
    frame = style.Frame(_GLOBAL_PM, style=frame_style)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    style.Label(frame, style=message_style, text=message).grid(row=0, column=0)
    btn_frame = style.Frame(frame, style=frame_style)
    for btn_text in buttons:
        btn = style.Button(btn_frame, style=button_style, text=btn_text, command=partial(btn_callback, btn_text))
        btn.pack(side=tk.LEFT, padx=2, pady=2)
    btn_frame.grid(row=1, column=0, sticky=tk.E)
    _GLOBAL_PM.create(frame, title, on_open=on_open, on_close=lambda: on_close(ret))
