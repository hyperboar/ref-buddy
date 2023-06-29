import os
import sys

from Env import Env
from image_metadata_controller import ImageMetadataController as Ctrl
from maintenance import assign_folder_tags, make_database_backup
from models.models_lump import Session


class ImageMetadataImporter:
    def __init__(self, db_path):
        pass

    def import_metadata(self, folder_path):
        formats = tuple(Env.IMPORT_FORMATS)
        sts = Ctrl.get_study_types()

        new_count = 0
        self.print_begin(f'Starting image import from folder "{folder_path}"')
        self.print_begin(f'Image formats to be imported: {formats}')

        make_database_backup(True)

        session = Session()

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
                    existing_metadata = Ctrl.get_by_path(file_path, session=session)
                    if not existing_metadata:
                        count += 1
                        new_count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, True)
                        Ctrl.create(file_path, sts, session=session)
                    else:
                        count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, False)
                except Exception as e:
                    print(f"\nError processing  {file_path}: {sys.exc_info()[0]}")
                    raise
            print(f"")

        if new_count > 0:
            print("")
            print(f"\rAssigning essential tags to new images...", end="")
            assign_folder_tags()
            print(f"\rAssigning essential tags to new images... Done", end="")

        print(f"\nImport completed! Found {new_count} new files.")

    @staticmethod
    def print_begin(msg):
        print(msg)

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
