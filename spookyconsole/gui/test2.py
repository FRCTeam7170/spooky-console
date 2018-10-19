
import tkinter as tk
from spookyconsole.gui.widgets import Gyro


root = tk.Tk()
Gyro(root).pack(fill=tk.BOTH, expand=True)
root.mainloop()
