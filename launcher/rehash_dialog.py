import tkinter as tk


class RehashDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Hash images")
        self.result = None

        # Create your custom buttons
        self.button1 = tk.Button(self, text="Rehash ALL images", command=self.hash_all)
        self.button2 = tk.Button(self, text="Hash only new images", command=self.hash_new)

        # Place the buttons in the dialog window
        self.button1.pack(side=tk.LEFT, padx=10, pady=10)
        self.button2.pack(side=tk.LEFT, padx=10, pady=10)

    def hash_all(self):
        self.result = "all"
        self.destroy()

    def hash_new(self):
        self.result = "new"
        self.destroy()
