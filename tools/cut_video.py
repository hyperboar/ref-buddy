import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime, timedelta
import json

class VideoAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotation App")
        self.root.geometry("500x600")

        self.current_row = 0
        # Video Path
        self.video_path_label = tk.Label(root, text="Video File:")
        self.video_path_label.grid(row=self.current_row, column=0, padx=10, pady=10)

        self.video_path_var = tk.StringVar()
        self.video_path_entry = tk.Entry(root, textvariable=self.video_path_var, width=40, state="disabled")
        self.video_path_entry.grid(row=self.current_row, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_video)
        self.browse_button.grid(row=self.current_row, column=2, padx=10, pady=10)

        self.current_row += 1

        # Import and Export Buttons
        self.import_button = tk.Button(root, text="Import Time", command=self.import_rows)
        self.import_button.grid(row=self.current_row, column=0, padx=10, pady=10)

        self.export_button = tk.Button(root, text="Export Time", command=self.export_rows)
        self.export_button.grid(row=self.current_row, column=2, padx=10, pady=10)

        self.current_row += 1

        # Export Bat Button
        self.export_bat_button = tk.Button(root, text="Export Bat", command=self.export_bat)
        self.export_bat_button.grid(row=self.current_row, column=1, padx=10, pady=10)

        self.current_row += 1

        # Add Row Button
        self.add_row_button = tk.Button(root, text="Add Row", command=self.add_row)
        self.add_row_button.grid(row=self.current_row, column=0, padx=10, pady=10)

        self.current_row += 1

        self.group_frame = tk.Frame(root)
        self.group_frame.grid(row=self.current_row, column=0, columnspan=4)

        self.current_row = 0
        # Table Header
        headers = ["Start Time", "End Time", "Short Note", "X"]
        for col, header in enumerate(headers):
            label = tk.Label(self.group_frame, text=header, font=("bold", 10))
            label.grid(row=self.current_row, column=col, padx=10, pady=5)

        # Table
        self.rows = []
        
        self.current_row += 1



    def browse_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        if file_path:
            self.video_path_var.set(file_path)
            self.video_path_entry.config(state="normal")

    def import_rows(self):
        # Import rows from a JSON file
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as json_file:
                rows_data = json.load(json_file)

            # Clear existing rows
            self.clear_table()

            # Add imported rows to the table
            for row_data in rows_data:
                self.add_row()
                self.rows[-1][0].delete(0, tk.END)
                self.rows[-1][1].delete(0, tk.END)
                self.rows[-1][2].delete(0, tk.END)
                self.rows[-1][0].insert(0, self.seconds_to_time(row_data[0]))
                self.rows[-1][1].insert(0, self.seconds_to_time(row_data[1]))
                self.rows[-1][2].insert(0, row_data[2])

    def export_rows(self):
        # Export rows to a JSON file
        rows_data = []
        for row in self.rows:
            start_time = row[0].get()
            end_time = row[1].get()
            short_note = row[2].get()
            rows_data.append((self.time_to_seconds(start_time), self.time_to_seconds(end_time), short_note))

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'w') as json_file:
                json.dump(rows_data, json_file, indent=2)

    def clear_table(self):
        # Clear all rows from the table
        for row in self.rows:
            for widget in row:
                widget.destroy()
        self.rows = []
        self.current_row = 2

    def add_row(self):

        default_values = ("00:00:00", "00:00:00", "Default Note")

        # Add a new row to the table
        start_time_entry = tk.Entry(self.group_frame, width=10)
        start_time_entry.grid(row=self.current_row, column=0, padx=5, pady=5)
        start_time_entry.insert(0, default_values[0])

        end_time_entry = tk.Entry(self.group_frame, width=10)
        end_time_entry.grid(row=self.current_row, column=1, padx=5, pady=5)
        end_time_entry.insert(0, default_values[1])

        short_note_entry = tk.Entry(self.group_frame, width=20)
        short_note_entry.grid(row=self.current_row, column=2, padx=5, pady=5)

        delete_button = tk.Button(self.group_frame, text="Delete", command=lambda: self.delete_row(start_time_entry))
        delete_button.grid(row=self.current_row, column=3, padx=5, pady=5)

        self.rows.append((start_time_entry, end_time_entry, short_note_entry, delete_button))
        self.current_row += 1

    def delete_row(self, start_time_hint):
        # Remove the specified row from the table
        rows = [r for r in self.rows if r[0] == start_time_hint]
        idx = self.rows.index(rows[0])

        for widget in self.rows[idx]:
            widget.destroy()

        del self.rows[idx]

    def time_to_seconds(self, time_str):
        # Convert time in "00:00:00" format to total seconds
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()

    def seconds_to_time(self, seconds):
        # Convert total seconds to time in "00:00:00" format
        return str(timedelta(seconds=seconds))

    def export_bat(self):
        # Get the data from the rows and execute the subprocess
        rows_data = []
        for row in self.rows:
            start_time = row[0].get()
            end_time = self.time_to_seconds(row[1].get()) - self.time_to_seconds(row[0].get())
            short_note = row[2].get()
            rows_data.append((start_time, end_time, short_note))
        
        path = os.path.expanduser('~/Desktop/123')
        if not os.path.exists(path):
            os.makedirs(path)

        # path = os.path.dirname(self.video_path_var.get())
        with (open(os.path.join(path, 'export.bat'), 'w') as f):
            i = 1

            for r in rows_data:
                out = os.path.join(path, f'{i:03}_{r[2]}.mp4')
                cmd = f'ffmpeg -i "{self.video_path_var.get()}" -ss {r[0]} -t {r[1]} "{out}"'
                print(cmd)
                i += 1
                f.write(cmd + '\n')
                # Execute subprocess with rows data as arguments
                # subprocess.run(cmd)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnnotationApp(root)
    root.mainloop()
