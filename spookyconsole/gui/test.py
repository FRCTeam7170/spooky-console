
import tkinter as tk
from spookyconsole.nt import serialize
import spookyconsole.gui.style as style
from spookyconsole.gui import core
from spookyconsole.gui import plot
from spookyconsole.gui import widgets
from spookyconsole.gui import popup
from spookyconsole import utils
import math
from functools import partial


def clamping_tan(val, max_):
    val = math.tan(val)
    if val > max_:
        return max_
    elif val < -max_:
        return -max_
    return val


def temp():
    if inst.isConnected():
        serialize.NTSerializer.from_entry(inst.getTable("/stuff").getEntry("1"), cache_size=0)
    else:
        gui.root.after(500, temp)


gui = core.GuiManager("Plot Tests")
style.init_fonts(gui.root)
popup.init_global_pm(gui.root)
# my_style = style.Style(bg=style.GRAY_SCALE_4, fg=style.GRAY_SCALE_E, font="FONT_SERIF_NORMAL",
#                        activebackground=style.GRAY_SCALE_4, selectcolor=style.GRAY_SCALE_4)
# plot.init_mpl_rcparams(my_style)
win, _ = gui.new_win(18, 18)  # , style=my_style)
win.protocol("WM_DELETE_WINDOW", gui.root.destroy)
win.grid.set_resize_protocol(core.Grid.RESIZE_PROTO_EXPAND_CELLS)

from networktables.instance import NetworkTablesInstance
inst = NetworkTablesInstance.create()
inst.startClient(("172.22.11.2", 1735))
ntb = widgets.DockableNTBrowser(win.grid, inst.getTable("/"))  # , style=my_style)
ntb.reload_when_connected(inst)
win.grid.register_dockable(ntb)
# gui.root.after(500, temp)

"""
p1 = plot.DockablePlot(win.grid, style=my_style)
win.grid.register_dockable(p1)
line = p1.figure.get_axes()[0].plot([], [])[0]
data1 = utils.xy_data_generator(math.cos, 5)
lu1 = plot.LiveUpdater(line, p1, feeder=lambda: next(data1), interval=500, max_data_cardinality=100)

p2 = plot.DockablePlot(win.grid, style=my_style)
win.grid.register_dockable(p2)
line = p2.figure.get_axes()[0].plot([], [])[0]
data2 = utils.xy_data_generator(math.sin, 5)
lu2 = plot.LiveUpdater(line, p2, feeder=lambda: next(data2), interval=500, max_data_cardinality=100)

p3 = plot.DockablePlot(win.grid, style=my_style)
win.grid.register_dockable(p3)
line = p3.figure.get_axes()[0].plot([], [])[0]
data3 = utils.xy_data_generator(partial(clamping_tan, max_=10), 5)
lu3 = plot.LiveUpdater(line, p3, feeder=lambda: next(data3), interval=500, max_data_cardinality=100)
"""

gui.root.mainloop()
