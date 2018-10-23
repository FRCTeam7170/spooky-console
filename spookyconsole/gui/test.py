
from spookyconsole.gui import core
from spookyconsole.gui import plot
from spookyconsole.gui import widgets
from spookyconsole.test import TableSim
from spookyconsole import utils
import math


def clamping_tan(val, max_):
    val = math.tan(val)
    if val > max_:
        return max_
    elif val < -max_:
        return -max_
    return val


gui = core.GuiManager("Plot Tests")
win = gui.new_win()
win.protocol("WM_DELETE_WINDOW", gui.root.destroy)
win.init_grid(10, 10).set_resize_protocol(core.Grid.RESIZE_PROTO_ADD_PADDING)
bib = widgets.DockableBooleanIndicatorBank(win.grid)
bib.add(0, 0, text="What1")
bib.add(0, 1, text="What2")
bib.add(1, 0, text="What3")
bib.add(1, 1, text="What4")
win.grid.register_dockable(bib)

"""
p1 = plot.DockablePlot(win.grid, style="ggplot")
win.grid.register_dockable(p1)
line = p1.figure.get_axes()[0].plot([], [])[0]
data1 = utils.xy_data_generator(math.cos, 5)
lu1 = plot.LiveUpdater(line, p1, feeder=lambda: next(data1), interval=500, max_data_cardinality=100)

p2 = plot.DockablePlot(win.grid)
win.grid.register_dockable(p2)
line = p2.figure.get_axes()[0].plot([], [])[0]
data2 = utils.xy_data_generator(math.sin, 5)
lu2 = plot.LiveUpdater(line, p2, feeder=lambda: next(data2), interval=500, max_data_cardinality=100)

p3 = plot.DockablePlot(win.grid)
win.grid.register_dockable(p3)
line = p3.figure.get_axes()[0].plot([], [])[0]
data3 = utils.xy_data_generator(partial(clamping_tan, max_=10), 5)
lu3 = plot.LiveUpdater(line, p3, feeder=lambda: next(data3), interval=500, max_data_cardinality=100)
"""

gui.root.mainloop()
