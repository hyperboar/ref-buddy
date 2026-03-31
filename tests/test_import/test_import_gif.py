import os

from app.models.models_lump import ImageMetadata
from launcher.image_metadata_importer import ImageMetadataImporter
from shared_utils.env import Env


def test_import_gif_additional_files_generated(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_gif')

    with session_real() as session:

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        im = session.query(ImageMetadata).first()
        zip_file = os.path.join(Env.TMP_PATH_GIF, f'{im.filename}.zip')
        json_file = os.path.join(Env.TMP_PATH_GIF, f'{im.filename}.json')

        assert os.path.exists(zip_file)
        assert os.path.exists(json_file)