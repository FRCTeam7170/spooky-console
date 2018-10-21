
import tkinter as tk


_tkButton = tk.Button
_tkCanvas = tk.Canvas
_tkCheckbutton = tk.Checkbutton
_tkEntry = tk.Entry
_tkFrame = tk.Frame
_tkLabel = tk.Label
_tkLabelFrame = tk.LabelFrame
_tkListbox = tk.Listbox
_tkRadiobutton = tk.Radiobutton
_tkScale = tk.Scale
_tkSpinbox = tk.Spinbox
_tkText = tk.Text


common_opts = set()
for k, v in globals().copy().items():
    if k.startswith("_tk"):
        common_opts = common_opts.union(v().configure().keys())
print(common_opts)
