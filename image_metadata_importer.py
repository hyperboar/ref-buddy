import sqlite3
import os
from image_metadata import ImageMetadata
from datetime import datetime
import sys


class ImageMetadataImporter:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def __del__(self):
        self.conn.close()

    def import_metadata(self, folder_path):

        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file_name in filenames:
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(dirpath, file_name)
                    file_path = os.path.relpath(file_path, folder_path)
                    print("File path:", file_path)
                    try:
                        existing_metadata = ImageMetadata.get_by_path(self.conn, file_path)
                        if not existing_metadata:
                            ImageMetadata.create(self.conn, file_path)
                        else:

                            print("File already recorded: ", file_path)
                    except Exception as e:
                        print(f"Error processing  {file_path}: {sys.exc_info()[0]}")
                        raise

if __name__ == '__main__':
    folder_path = sys.argv[1]
    if not os.path.isabs(folder_path):
        print("Error: Please provide a valid absolute path to the folder.")
        sys.exit(1)

    ImageMetadataImporter.import_images(folder_path)