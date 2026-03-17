import os
import sys
import time
from datetime import datetime, timedelta

from shared_utils.env import Env
from app.services.image_metadata_controller import ImageMetadataController as Ctrl
from shared_utils.maintenance import assign_folder_tags, make_database_backup, generate_thumbs, assign_animation_tags, \
    assign_video_extra_data, gif_split
from app.models import Session
from app.models.models_lump import Path, ImageMetadata
from shared_utils.nice_print import NicePrinter


class ImageMetadataImporter:
    def __init__(self):
        self.np = NicePrinter()

    def import_metadata(self, folder_path):
        folder_path = os.path.normpath(folder_path)
        formats = tuple(Env.IMPORT_FORMATS)
        sts = Ctrl.get_categories()

        start_time = time.time()
        new_count = 0
        self.np.header(f'Starting image import from folder "{folder_path}"')
        self.np.header(f'Image formats to be imported: {formats}')

        self.np.step_up()

        session = Session()

        time_of_import = datetime.now()
        # -1 just to make sure we're in the past
        update_time = time_of_import - timedelta(seconds=1)

        for dir_path, dir_names, filenames in os.walk(folder_path):
            count = 0
            max_count = len(filenames)
            msg_dir = f'Importing "{os.path.relpath(dir_path, folder_path)}"...'

            dir_path = os.path.normpath(dir_path)
            rel_path = Path.path_serialize(os.path.relpath(dir_path, folder_path))
            path_obj = session.query(Path).filter(Path.path_raw == rel_path).first()
            if path_obj is not None:
                # check and modify update time
                path_mtime = int(os.path.getmtime(dir_path))
                mdt = datetime.fromtimestamp(path_mtime)
                pm_diff = mdt - path_obj.last_updated
                if pm_diff.total_seconds() < 1.0:
                    continue
                else:
                    self.np.line(msg_dir, replace=True)

                    path_obj.last_updated = mdt
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
                    self.np.header(f'\nError processing  {file_path}: {sys.exc_info()[0]}. {e}')
                    raise

            if path_obj is not None:
                self.np.line('')

        self.np.step_down()
        if new_count == 0:
            self.np.header(f'File search completed! No new images found.')
            session.rollback()
        else:
            self.np.header(f'File search completed! Found {new_count} new files.')
            make_database_backup(marker='before_import', force=True)
            session.commit()

            self.np.step_up()

            assign_folder_tags(start_at=update_time, session=session, printer=self.np)
            assign_animation_tags(start_at=update_time, session=session, printer=self.np)
            assign_video_extra_data(start_at=update_time, session=session, printer=self.np)
            make_database_backup(marker='after_import', force=True)
            generate_thumbs(start_at=update_time)
            gif_split(force_all=False)

            self.np.step_down()

        self.np.header(f'Import completed in {int(time.time() - start_time)} seconds.')

    def print_progress(self, msg_dir, file_name: str, cur: int, total: int, is_new: bool):
        if is_new:
            self.np.line(f'{msg_dir} ({cur}/{total}) New "{file_name}"', True)
        else:
            pass
            # print(f'\r{msg_dir} ({cur}/{total}) File exists '{file_name}'', end='')


if __name__ == '__main__':
    path = sys.argv[1]
    if not os.path.isabs(path):
        print('Error: Please provide a valid absolute path to the folder.')
        sys.exit(1)

    ImageMetadataImporter.import_images(path)
