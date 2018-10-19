
from .core import ScrollCanvas
from .plot import Plot, LiveUpdater
from ..utils import xy_data_generator
import tkinter as tk
import math

root = tk.Tk()
sc = ScrollCanvas(root, 5000, 5000)
sc.frame.pack(expand=True, fill=tk.BOTH)

plot = Plot(sc)
line = plot.figure.get_axes()[0].plot([], [])[0]
data = xy_data_generator(math.cos, 5)
lu = LiveUpdater(line, plot, feeder=lambda: next(data), interval=50, max_data_cardinality=100)
sc.create_window(10, 10, width=150, height=100, window=plot, anchor=tk.NW)

root.mainloop()
