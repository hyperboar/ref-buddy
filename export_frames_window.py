import os.path
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from Env import Env

# we might need to install ImageMagic first https://imagemagick.org/script/download.php
IMAGEMAGIC_URL = "https://imagemagick.org/script/download.php"
try:
    from wand.image import Image
except ImportError:
    Image = None


class ExportFramesWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Export frames")

        self.create_widgets()

    def create_widgets(self):
        # Create widgets
        self.file_label = tk.Label(self, text="File path:")
        self.file_entry = tk.Entry(self, width=50)
        self.file_button = tk.Button(self, text="Browse", command=self.browse_file)

        self.fps_label = tk.Label(self, text="FPS (ffmpeg target/Webp to skip):")
        self.fps_entry = tk.Entry(self, width=10, validate="key")
        self.fps_entry.config(validatecommand=(self.fps_entry.register(self.validate_int), "%P"))
        self.fps_entry.insert(0, Env.DEFAULT_FPS_SPLIT)

        self.video_btn = tk.Button(self, text="Export", command=self.split_file)

        # Layout widgets
        self.file_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        self.file_button.grid(row=0, column=2, padx=10, pady=10)

        self.fps_label.grid(row=1, column=0, padx=10, pady=10)
        self.fps_entry.grid(row=1, column=1, padx=10, pady=10)

        self.video_btn.grid(row=2, column=1, padx=10, pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(initialdir="", title="Select a File",
                                              filetypes=[("Sequences", "*.gif *.webp *.webm *.mp4 *.avi *.mov"), ("All files", "*.*")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)
        self.focus_force()

    def split_file(self):

        if not os.path.exists(self.file_entry.get()):
            print('Provide a file first.')
            return

        input_file = self.file_entry.get()
        filename, ext = os.path.splitext(os.path.basename(input_file))

        new_dir = os.path.join(os.path.dirname(input_file), filename)

        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)

        os.mkdir(new_dir)

        match ext:
            case ".webp":
                self.split_webp(input_file, os.path.join(new_dir, filename))
                pass
            case ".webm" | ".gif" | ".mp4" | ".avi" | ".mov":
                self.split_ffmpeg(input_file, os.path.join(new_dir, filename))
                pass

    def split_webp(self, input_file, output_file):

        if Image is None:
            messagebox.showerror("ImageMagic is not installed.", f"To export .webp files you need to install ImageMagic libs first. Use this link {IMAGEMAGIC_URL}")
            return

        with Image(filename=input_file) as img:
            skip = int(self.fps_entry.get())
            for i, frame in enumerate(img.sequence):
                with Image(frame) as f:
                    if (i % skip) != 0:
                        continue
                    f.save(filename=f'{os.path.join(output_file)}_{i}.png')

    def split_ffmpeg(self, input_file, filename):

        # if ffmpeg_ver is None:
        #     messagebox.showerror("ImageMagic is not installed.", f"To export .webp files you need to install ImageMagic libs first. Use this link {IMAGEMAGIC_URL}")
        #     return

        output_file = os.path.join(filename + "_%04d.png")

        command = ["ffmpeg", "-i", input_file, "-vf", f"fps={self.fps_entry.get()}", output_file]
        print(command)

        subprocess.call(command)
        pass

    def validate_int(self, new_value):
        if new_value == "":
            return True
        try:
            int(new_value)
            return True
        except ValueError:
            return False