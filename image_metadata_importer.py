import sqlite3
import os
from image_metadata import ImageMetadata
import sys


class ImageMetadataImporter:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def __del__(self):
        self.conn.close()

    def import_metadata(self, folder_path):
        formats = ('.png', '.jpg', '.jpeg', '.webp')
        ImageMetadata.static_initialize(self.conn)
        sts = ImageMetadata.get_study_types(self.conn)

        new_count = 0

        for dir_path, dir_names, filenames in os.walk(folder_path):
            count = 0
            max_count = len(filenames)
            msg_dir = f"Importing '{dir_path}'..."
            self.print_total(msg_dir, len(filenames))
            for file_name in filenames:
                if not file_name.endswith(formats):
                    continue
                file_path = os.path.join(dir_path, file_name)
                file_path = os.path.relpath(file_path, folder_path)
                try:
                    existing_metadata = ImageMetadata.get_by_path(self.conn, file_path)
                    if not existing_metadata:
                        count += 1
                        new_count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, True)
                        ImageMetadata.create(self.conn, file_path, sts)
                    else:
                        count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, False)
                except Exception as e:
                    print(f"Error processing  {file_path}: {sys.exc_info()[0]}")
                    raise
            print(f"")

        print(f"\nImport completed! Found {new_count} new files.")

    @staticmethod
    def print_total(msg_dir, total: int):
        print(f"\r{msg_dir}. {total} files in this folder", end='')

    @staticmethod
    def print_progress(msg_dir, file_name: str, cur: int, total: int, is_new: bool):
        if is_new:
            print(f"\r{msg_dir} ({cur}/{total}) New '{file_name}'", end='')
        else:
            pass
            # print(f"\r{msg_dir} ({cur}/{total}) File exists '{file_name}'", end='')


if __name__ == '__main__':
    path = sys.argv[1]
    if not os.path.isabs(path):
        print("Error: Please provide a valid absolute path to the folder.")
        sys.exit(1)

    ImageMetadataImporter.import_images(path)
