
import tkinter as tk
import spookyconsole.gui.style as style
import spookyconsole.gui.popup as popup


def on_open():
    print("WHOO! OPENED!")


def on_close(resp):
    print("RESP: {}".format(resp))


def do_stuff():
    popup.dialog("Whats this?", "Uhh, no buttons?", popup.BUTTONS_YES_NO_CANCEL, on_open=on_open, on_close=on_close,
                 frame_style=my_style, message_style=my_style, button_style=btn_style)


root = tk.Tk()
root.title("ROOT")
style.init_fonts(root)
popup.init_global_pm(root)

my_style = style.Style(bg=style.GRAY_SCALE_5, fg=style.GRAY_SCALE_E)
btn_style = style.Style(my_style, relief=tk.GROOVE, activebackground=style.GRAY_SCALE_4,
                        activeforeground=style.GRAY_SCALE_E)

style.Button(root, style=btn_style, text="Click me", command=do_stuff).pack()

root.mainloop()
