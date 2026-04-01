import os
import sys
import time
from datetime import datetime, timedelta, timezone

from shared_utils.backup import make_database_backup
from shared_utils.env import Env
from app.services.image_metadata_controller import ImageMetadataController as Ctrl
from shared_utils.generators import assign_folder_tags, generate_thumbs, assign_animation_tags, \
    assign_video_extra_data, gif_split
from app.models import Session
from app.models.models_lump import Path, ImageMetadata
from shared_utils.nice_print import NicePrinter


class ImageMetadataImporter:
    def __init__(self):
        self.np = NicePrinter()

        self.time_of_import = datetime.now(tz=timezone.utc)
        # -1 just to make sure we're in the past
        self.update_time = self.time_of_import - timedelta(seconds=1)

        self.used = False

    def import_metadata(self, import_from_path:str) -> None:

        if self.used:
            raise Exception('ImageMetadataImporter can only be used once!')
        self.used = True

        import_from_path = os.path.normpath(import_from_path)
        formats = tuple(Env.IMPORT_FORMATS)

        start_time = time.time()
        new_count = 0

        self.np.header(f'Starting image import from folder "{import_from_path}"')
        self.np.header(f'Image formats to be imported: {formats}')

        with Session() as session:
            cats = Ctrl.get_categories(session)

            self.np.step_up()

            for dir_path, dir_names, filenames in os.walk(import_from_path):
                files_count = len(filenames)
                if files_count == 0: continue

                dir_path = os.path.normpath(dir_path)
                rel_path = Path.path_serialize(os.path.relpath(dir_path, import_from_path))

                dir_cat = next((c for c in cats if rel_path.startswith(c.category)), None)

                if dir_cat is None: continue              # skip if relevant category not found
                if rel_path == dir_cat.category: continue # skip category folder itself
                if not any(fn.endswith(formats) for fn in filenames): continue # skip when no relevant files found

                msg_dir = f'Importing "{rel_path}"...'
                dir_count = 0

                path = session.query(Path).filter(Path.path_raw == rel_path).first()
                if path is None:
                    path = Path(path_raw=rel_path)
                    session.add(path)
                    session.flush()

                # check and modify update time
                path_mtime = int(os.path.getmtime(dir_path))
                mdt = datetime.fromtimestamp(path_mtime, tz=timezone.utc)
                pm_diff = mdt - path.last_updated
                if pm_diff.total_seconds() < 1.0:
                    continue
                else:
                    path.last_updated = mdt
                    self.np.line(msg_dir, replace=True)

                for fn in filenames:
                    if not fn.endswith(formats): continue

                    file_path = Path.path_serialize(os.path.join(rel_path, fn))
                    try:
                        found = Ctrl.get_by_path(file_path, session=session)
                        if found is None:
                            new_count += 1
                            # Ctrl.create_on_import(file_path, cats, time_of_import, session=session)
                            source_type = ImageMetadata.source_type_by_path(file_path)

                            # print(f"inserting {(path_id, ctg.id, file)} for path '{new_path}'")

                            new_image = ImageMetadata(path_id=path.id, category_id=dir_cat.id, filename=fn,
                                                      source_type_id=source_type, imported_at=self.time_of_import)
                            session.add(new_image)

                            session.flush()
                        dir_count += 1
                        self.print_progress(msg_dir, fn, dir_count, files_count, found is None)
                    except Exception as e:
                        self.np.header(f'\nError processing  {file_path}: {sys.exc_info()[0]}. {e}')
                        raise

                if path is not None:
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

                self._additional_processing(session)

                make_database_backup(marker='after_import', force=True)

                generate_thumbs(start_at=self.update_time)
                gif_split(force_all=False)

                self.np.step_down()

            self.np.header(f'Import completed in {int(time.time() - start_time)} seconds.')

    def _additional_processing(self, session):
        assign_folder_tags(start_at=self.update_time, session=session, printer=self.np)
        assign_animation_tags(start_at=self.update_time, session=session, printer=self.np)
        assign_video_extra_data(start_at=self.update_time, session=session, printer=self.np)

    def print_progress(self, msg_dir, file_name: str, cur: int, total: int, is_new: bool):
        if is_new:
            self.np.line(f'{msg_dir} ({cur}/{total}) New "{file_name}"', True)
        else:
            pass
            # print(f'\r{msg_dir} ({cur}/{total}) File exists '{file_name}'', end='')


if __name__ == '__main__':
    path_ = sys.argv[1]
    if not os.path.isabs(path_):
        print('Error: Please provide a valid absolute path to the folder.')
        sys.exit(1)
    importer = ImageMetadataImporter()
    importer.import_metadata(path_)
