import tkinter as tk

from launcher.main_window import MainWindow
from shared_utils.maintenance import create_required_folders, create_new_db


create_required_folders()
create_new_db()

root = tk.Tk()
launcher = MainWindow(master=root)
launcher.mainloop()
