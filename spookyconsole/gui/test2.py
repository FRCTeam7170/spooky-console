
import tkinter as tk
from spookyconsole.gui.widgets import NTBrowser, TableSim


table = TableSim({"E1": "E"*200, "E2": 2, "E3": 3, "T1": {"T1E1": 1, "T1E2": 2}})

root = tk.Tk()
NTBrowser(root, table).pack(fill=tk.BOTH, expand=True)
root.mainloop()
