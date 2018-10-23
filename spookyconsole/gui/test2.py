
import tkinter as tk
from spookyconsole.gui import widgets


root = tk.Tk()

bib = widgets.BooleanIndicatorLabelledBank(root, "Four Things", labelanchor=tk.N)
bib.add(0, 0, text="What1")
bib.add(0, 1, text="What2")
bib.add(1, 0, text="What3")
bib.add(1, 1, text="What4")

bib.labelled_frame.pack()

root.mainloop()
