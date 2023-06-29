import os
import subprocess
import sys
import webbrowser
import tkinter as tk
from tkinter import messagebox

from export_frames_window import ExportFramesWindow

from image_metadata_importer import ImageMetadataImporter
from maintenance import generate_thumbs, rehash_images, mark_all_lost, relink_lost_images, cleanup_lost_images, \
    make_database_backup
from Env import Env
from rehash_dialog import RehashDialog


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Drawing Gallery Tool")
        self.master.geometry("300x200")
        self.pack()

        self.gallery_url = f"http://localhost:{Env.SERVER_PORT}"

        self.create_widgets()
        self.create_menus()

        self.web_process = None

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


        # Check if the database file exists
        if not os.path.isfile(Env.DB_FILE):
            messagebox.showerror("Error", "Database file not found. Please run the import first.")
            self.server_button["state"] = "disabled"
            # self.quit()

    def create_widgets(self):
        self.server_button = tk.Button(self)
        self.server_button["text"] = "Launch Server"
        self.server_button["command"] = self.launch_server
        self.server_button.pack(side="top", pady=20)

        self.link = tk.Label(self, text="Go to gallery")
        self.link["state"] = "disabled"
        self.link.pack(pady=10)
        self.link.bind("<Button-1>", self.go_to_gallery)
        self.link.config(fg="blue", cursor="hand2", font=("Arial", 12, "underline"))

        # quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        # quit_button.pack(side="bottom")

    def create_menus(self):
        self.menu_bar = tk.Menu(self.master)

        # create file menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Import images", command=self.import_images)
        file_menu.add_command(label="Exit", command=root.quit)

        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # create maintenance menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Export frames from file", command=self.open_ffmpeg_window)
        tools_menu.add_separator()
        tools_menu.add_command(label="Generate thumbs", command=generate_thumbs)
        tools_menu.add_command(label="Rehash all images", command=self.rehash_options)
        tools_menu.add_separator()
        tools_menu.add_command(label="Find lost images", command=mark_all_lost)
        tools_menu.add_command(label="Relink lost images", command=relink_lost_images)
        tools_menu.add_separator()
        tools_menu.add_command(label="Cleanup thumbs", command=cleanup_lost_images)

        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)

        self.master.config(menu=self.menu_bar)

    def import_images(self):
        if not os.path.exists(Env.IMAGES_PATH):
            messagebox.showinfo("Nope", f'Folder at path "{Env.IMAGES_PATH}" does not exist.')
            return

        try:
            importer = ImageMetadataImporter(Env.DB_FILE)
            importer.import_metadata(Env.IMAGES_PATH)
        except Exception as e:
            messagebox.showinfo("Nope", "Something went wrong. Check logs for details.")
            raise

        messagebox.showinfo("Success", "Images imported successfully.")

    def open_ffmpeg_window(self):
        self.ffmpeg = ExportFramesWindow(self.master)

    def launch_server(self):
        if sys.platform == 'win32':
            bin_fldr = "Scripts"
        else:
            bin_fldr = "bin"
        self.web_process = subprocess.Popen([os.path.join(sys.prefix, bin_fldr, 'python'), 'server.py'], cwd=os.getcwd())
        self.link["state"] = "normal"
        self.server_button["state"] = "disabled"

    def go_to_gallery(self, test):
        print(test)
        webbrowser.open(self.gallery_url)

    def rehash_options(self):
        dialog = RehashDialog(root)
        self.master.wait_window(dialog)
        result = dialog.result
        dialog.destroy()

        match result:
            case "all":
                print("\nRehashing ALL images...")
                rehash_images(rehash_all=True)
            case "new":
                print("\nHashing new images...")
                rehash_images(rehash_all=False)

    def on_closing(self):
        self.on_app_exit()
        self.master.quit()

    def on_app_exit(self):
        if self.web_process is not None and self.web_process.poll() is None:
            self.web_process.terminate()


if __name__ == "__main__":
    make_database_backup()

    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()
