import tkinter as tk

from launcher.main_window import MainWindow
from shared_utils.generators import create_required_folders, create_new_db

def create_window(testing=False) -> MainWindow:
    create_required_folders()
    create_new_db()

    root = tk.Tk()
    launcher = MainWindow(master=root)

    if not testing:
        launcher.mainloop()

    return launcher