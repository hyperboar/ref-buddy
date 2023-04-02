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

        for dir_path, dir_names, filenames in os.walk(folder_path):
            count = 0
            max_count = len(filenames)
            print(f"Importing '{dir_path}'...")
            for file_name in filenames:
                if file_name.endswith(formats):
                    file_path = os.path.join(dir_path, file_name)
                    file_path = os.path.relpath(file_path, folder_path)
                    try:
                        existing_metadata = ImageMetadata.get_by_path(self.conn, file_path)
                        if not existing_metadata:
                            count += 1
                            print(f"\r({count}/{max_count}) New '{file_path}'", end='')
                            ImageMetadata.create(self.conn, file_path, sts)
                        else:
                            count += 1
                            print(f"\r({count}/{max_count}) File exists '{file_path}'", end='')
                    except Exception as e:
                        print(f"Error processing  {file_path}: {sys.exc_info()[0]}")
                        raise
            print(f"")


if __name__ == '__main__':
    path = sys.argv[1]
    if not os.path.isabs(path):
        print("Error: Please provide a valid absolute path to the folder.")
        sys.exit(1)

    ImageMetadataImporter.import_images(path)
