import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from image_metadata_importer import ImageMetadataImporter
from image_metadata import ImageMetadata
import Env


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Drawing Gallery Tool")
        self.master.geometry("300x200")
        self.pack()

        self.gallery_url = f"http://localhost:{Env.SERVER_PORT}"

        self.create_widgets()

        # Check if the database file exists
        if not os.path.isfile(Env.DB_FILE):
            messagebox.showerror("Error", "Database file not found. Please run the import first.")
            self.server_button["state"] = "disabled"
            # self.quit()

    def create_widgets(self):
        self.import_button = tk.Button(self)
        self.import_button["text"] = "Import Images"
        self.import_button["command"] = self.import_images
        self.import_button.pack(side="top")

        self.server_button = tk.Button(self)
        self.server_button["text"] = "Launch Server"
        self.server_button["command"] = self.launch_server
        self.server_button.pack(side="top")

        self.link = tk.Label(root, text="Go to gallery")
        self.link["state"] = "disabled"
        self.link.pack(pady=20)
        self.link.bind("<Button-1>", self.go_to_gallery)
        self.link.config(fg="blue", cursor="hand2", font=("Arial", 12, "underline"))

        # quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        # quit_button.pack(side="bottom")

    def import_images(self):
        # Ask user to select a folder
        folder_path = filedialog.askdirectory()
        if folder_path:
            importer = ImageMetadataImporter(Env.DB_FILE)
            importer.import_metadata(folder_path)
            messagebox.showinfo("Success", "Images imported successfully.")

    def launch_server(self):
        subprocess.Popen(["python", "server.py"], cwd=os.getcwd())
        self.link["state"] = "normal"
        self.server_button["state"] = "disabled"

    def go_to_gallery(self, test):
        print(test)
        webbrowser.open(self.gallery_url)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()
