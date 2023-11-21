import os
import sys
import time
from datetime import datetime

from Env import Env
from image_metadata_controller import ImageMetadataController as Ctrl
from maintenance import assign_folder_tags, make_database_backup, generate_thumbs, rehash_images, assign_animation_tags
from models.models_lump import Session, Path, ImageMetadata


class ImageMetadataImporter:
    def __init__(self):
        pass

    def import_metadata(self, folder_path):
        folder_path = os.path.normpath(folder_path)
        formats = tuple(Env.IMPORT_FORMATS)
        sts = Ctrl.get_study_types()

        start_time = time.time()
        new_count = 0
        self.print_begin(f'Starting image import from folder "{folder_path}"')
        self.print_begin(f'Image formats to be imported: {formats}')

        make_database_backup(marker='before_import', force=True)

        session = Session()

        time_of_import = datetime.now()

        for dir_path, dir_names, filenames in os.walk(folder_path):
            count = 0
            max_count = len(filenames)
            msg_dir = f'Importing "{os.path.relpath(dir_path, folder_path)}"...'
            self.print_total(msg_dir, len(filenames))

            dir_path = os.path.normpath(dir_path)
            rel_path = Path.path_serialize(os.path.relpath(dir_path, folder_path))
            path_obj = session.query(Path).filter(Path.path_raw == rel_path).first()
            if path_obj is not None:
                existing_files = [im.filename for im in session.query(ImageMetadata).filter(ImageMetadata.path_id == path_obj.id)]
                filenames = [f for f in filenames if f not in existing_files]

            for file_name in filenames:
                if not file_name.endswith(formats):
                    continue
                file_path = Path.path_serialize(os.path.join(rel_path, file_name))
                try:
                    existing_metadata = Ctrl.get_by_path(file_path, session=session)
                    if not existing_metadata:
                        count += 1
                        new_count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, True)
                        Ctrl.create(file_path, sts, time_of_import, session=session)
                    else:
                        count += 1
                        self.print_progress(msg_dir, file_name, count, max_count, False)
                except Exception as e:
                    print(f'\nError processing  {file_path}: {sys.exc_info()[0]}. {e}')
                    raise
            print(f'')

        if new_count == 0:
            print(f'Images import completed! Found {new_count} new files.')
        else:
            session.commit()
            print(f'Images import completed! Found {new_count} new files.')
            assign_folder_tags(session)
            assign_animation_tags(session)
            rehash_images(False)
            make_database_backup(marker='after_import', force=True)
            generate_thumbs()

        print(f'Import completed ({int(time.time() - start_time)} sec).')

    @staticmethod
    def print_begin(msg):
        print(msg)

    @staticmethod
    def print_total(msg_dir, total: int):
        print(f'\r{msg_dir}. {total} files in this folder', end='')

    @staticmethod
    def print_progress(msg_dir, file_name: str, cur: int, total: int, is_new: bool):
        if is_new:
            print(f'\r{msg_dir} ({cur}/{total}) New "{file_name}"', end='')
        else:
            pass
            # print(f'\r{msg_dir} ({cur}/{total}) File exists '{file_name}'', end='')


if __name__ == '__main__':
    path = sys.argv[1]
    if not os.path.isabs(path):
        print('Error: Please provide a valid absolute path to the folder.')
        sys.exit(1)

    ImageMetadataImporter.import_images(path)
