
from spookyconsole.gui import core
from spookyconsole.gui import plot
from spookyconsole.gui import widgets
from spookyconsole import utils
import math
import matplotlib.style as s
print(s.available)


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

win.grid.register_dockable(widgets.DockableGyro(win.grid, 2, 2))

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
