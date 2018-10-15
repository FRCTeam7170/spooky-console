
import math
import itertools
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation


def xydata_generator(func, div):
    for num in itertools.count():
        num = num / div
        yield num, func(num)


class Plot(tk.Frame):

    def __init__(self, master, data_source, interval=100, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.data_source = data_source
        self.figure = Figure((5, 5), 100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.nav_bar = NavigationToolbar2Tk(self.canvas, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.axis = self.figure.add_subplot(111)
        self.x_data = []
        self.y_data = []
        self.line = self.axis.plot([], [])[0]  # Axes.plot returns a list
        # Set the data to a mutable type so we only need to append to it then force the line to invalidate its cache
        self.line.set_data(self.x_data, self.y_data)
        self.ani = FuncAnimation(self.figure, self.update_plot, interval=interval)

    def update_plot(self, _):
        x, y = next(self.data_source)  # (realistically the data source wouldn't be restricted to be a generator)
        # Because the Line2D object stores a reference to the two lists, we need only update the lists and signal
        # that the line needs to be updated.
        self.x_data.append(x)
        self.y_data.append(y)
        self.line.recache_always()
        self._refit_artists()

    def _refit_artists(self):
        # self.axis.set_xlim(min(self.x_data), max(self.x_data))
        # self.axis.set_ylim(min(self.y_data), max(self.y_data))
        self.axis.relim()
        self.axis.autoscale_view()

    def _eun(self, _):
        self.axis.set_autoscale_on(True)
        print("EUN")


root = tk.Tk()
data = xydata_generator(math.sin, 5)
plot = Plot(root, data)
root.bind("a", plot._eun)
plot.pack(fill=tk.BOTH, expand=True)
root.mainloop()
