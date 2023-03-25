import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from image_metadata_importer import ImageMetadataImporter
from image_metadata import ImageMetadata

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the values of DB_PATH and DB_NAME from the environment
DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))
IMAGES_PATH = os.getenv('IMAGES_PATH')


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Image Metadata")
        self.master.geometry("300x200")
        self.pack()

        # Check if the database file exists
        if not os.path.isfile(DB_FILE):
            messagebox.showerror("Error", "Database file not found. Please run the import first.")
            self.quit()

        self.create_widgets()

    def create_widgets(self):
        self.import_button = tk.Button(self)
        self.import_button["text"] = "Import Images"
        self.import_button["command"] = self.import_images
        self.import_button.pack(side="top")

        self.server_button = tk.Button(self)
        self.server_button["text"] = "Launch Server"
        self.server_button["command"] = self.launch_server
        self.server_button.pack(side="top")

        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit_button.pack(side="bottom")

    def import_images(self):
        # Ask user to select a folder
        folder_path = filedialog.askdirectory()
        if folder_path:
            importer = ImageMetadataImporter(DB_FILE)
            importer.import_metadata(folder_path)
            messagebox.showinfo("Success", "Images imported successfully.")

    def launch_server(self):
        subprocess.Popen(["python", "server.py"], cwd=os.getcwd())

    def open_web_page(self):
        webbrowser.open(ImageMetadata.get_random_image().to_html())

root = tk.Tk()
app = MainWindow(master=root)
app.mainloop()