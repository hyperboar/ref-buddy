import json
import os

from app.models.models_lump import ImageMetadata
from launcher.image_metadata_importer import ImageMetadataImporter
from shared_utils.env import Env

def test_import_video_extra(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_video')

    with session_real() as session:
        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        im = session.query(ImageMetadata).first()
        assert len(im.extras) == 1

        data = json.loads(im.extras[0].data)
        assert 'dur' in data
        assert 'fps' in data

def test_import_video_not_treated_as_gif(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_video')

    with session_real() as session:
        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        im = session.query(ImageMetadata).first()
        zip_file = os.path.join(Env.TMP_PATH_GIF, f'{im.filename}.zip')
        json_file = os.path.join(Env.TMP_PATH_GIF, f'{im.filename}.json')

        assert not os.path.exists(zip_file)
        assert not os.path.exists(json_file)