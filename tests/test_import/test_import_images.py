import os
import shutil

import pytest

from app.models.models_lump import ImageMetadata, Path
from launcher.image_metadata_importer import ImageMetadataImporter
from shared_utils.env import Env
from tests.fixtures.data import add_1_category

@pytest.mark.parametrize('assets_dir, expected_count', [
    ('assets_import_images_single_dir', 2),
    ('assets_import_images_mult_dir', 4),
    ('assets_import_images_nested_dir', 4),
    ('assets_import_images_gif', 1),
    ('assets_import_images_wrong_dir', 1),
    ('assets_import_images_video', 1),
    ('assets_import_images_unsupported_format', 1),
])
def test_import_images_and_count(session_real, copy_assets_to_env, assets_dir, expected_count):

    copy_assets_to_env(assets_dir)

    with session_real() as session:
        count = session.query(ImageMetadata).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == expected_count

def test_import_images_mult_category_known(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_mult_category')

    with session_real() as session:
        count = session.query(ImageMetadata).count()
        assert count == 0

        add_1_category(session)

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 4

def test_import_images_mult_category_un_known(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_mult_category')

    with session_real() as session:
        count = session.query(ImageMetadata).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 2

@pytest.mark.parametrize('assets_dir, filename, expected_source_type_id', [
    ('assets_import_images_single_dir', 'Lenna_1.jpg', 1),
    ('assets_import_images_gif', 'Lenna_6_source_gif.gif', 2),
    ('assets_import_images_video', 'Lenna_5_source_mp4.mp4.gif', 3),
])
def test_import_images_source_type(session_real, copy_assets_to_env, assets_dir, filename, expected_source_type_id):
    copy_assets_to_env(assets_dir)

    with session_real() as session:
        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        item = session.query(ImageMetadata).filter(ImageMetadata.filename == filename).first()
        assert item.source_type_id == expected_source_type_id

def test_import_images_category_id(session_real, copy_assets_to_env):
    copy_assets_to_env('assets_import_images_mult_category')

    with session_real() as session:

        add_1_category(session)

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        get_item = lambda session, fn: session.query(ImageMetadata).filter(ImageMetadata.filename == fn).first()

        assert get_item(session, 'Lenna_1.jpg').category_id == 1
        assert get_item(session, 'Lenna_2.jpg').category_id == 1
        assert get_item(session, 'Lenna_3.jpg').category_id == 2
        assert get_item(session, 'Lenna_4.jpg').category_id == 2

def test_import_images_path_id(session_real, copy_assets_to_env):
    copy_assets_to_env('assets_import_images_mult_category')

    with session_real() as session:
        add_1_category(session)

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        get_item = lambda session, fn: session.query(ImageMetadata).filter(ImageMetadata.filename == fn).first()

        assert get_item(session, 'Lenna_1.jpg').path_id == 1
        assert get_item(session, 'Lenna_2.jpg').path_id == 1
        assert get_item(session, 'Lenna_3.jpg').path_id == 2
        assert get_item(session, 'Lenna_4.jpg').path_id == 2

@pytest.mark.parametrize('assets_dir', [
    'assets_import_images_mult_dir',
    'assets_import_images_gif',
    'assets_import_images_video',
])
def test_import_images_thumbs_generated(session_real, copy_assets_to_env, assets_dir):

    copy_assets_to_env(assets_dir)

    with session_real() as session:

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        imgs = session.query(ImageMetadata).all()
        thumbs = [f'{im.image_id}.jpg' for im in imgs]

        thumb_files = [file for file in os.listdir(Env.THUMB_PATH)]

        assert len(thumbs) == len(thumb_files)
        assert all([t in thumb_files for t in thumbs])

def test_import_images_same_imported_at_timestamp(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_mult_dir')

    with session_real() as session:
        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        imgs = session.query(ImageMetadata).all()
        imported_at = imgs[0].imported_at
        is_same_time = lambda t1, t2: abs((t1 - t2).total_seconds()) < 1.0
        assert all([ is_same_time(imported_at, im.imported_at) for im in imgs])

@pytest.mark.parametrize('assets_dir, expected_count', [
    ('assets_import_images_single_dir', 1),
    ('assets_import_images_mult_dir', 2),
    ('assets_import_images_nested_dir', 2),
    ('assets_import_images_empty_dir', 1),
])
def test_import_path_created(session_real, copy_assets_to_env, assets_dir, expected_count):

    copy_assets_to_env(assets_dir)

    with session_real() as session:
        count = session.query(Path).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(Path).count()
        assert count == expected_count

@pytest.mark.skip(reason="To Be Implemented")
@pytest.mark.parametrize('assets_dir, expected_count', [
    ('assets_import_images_nested_dir', 1),
])
def test_import_path_created_1(session_real, copy_assets_to_env, assets_dir, expected_count):

    copy_assets_to_env(assets_dir)

    with session_real() as session:
        count = session.query(Path).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(Path).count()
        assert count == expected_count

@pytest.mark.skip(reason="To Be Implemented")
def test_import_path_only_top_created_for_nested(session_real, copy_assets_to_env):
    copy_assets_to_env('assets_import_images_nested_dir')

    with session_real() as session:
        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        paths = session.query(Path).all()
        assert len(paths) == 1
        assert paths[0].path == os.path.normpath('everything/dir_1')

def test_import_path_empty_not_created(session_real, copy_assets_to_env):
    copy_assets_to_env('assets_import_images_empty_dir')

    with session_real() as session:
        count = session.query(Path).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(Path).count()
        assert count == 1

def test_import_images_same_images_not_imported_again(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_single_dir')

    with session_real() as session:
        count = session.query(ImageMetadata).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 2

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 2

def test_import_images_new_added_to_imported_folder(session_real, copy_assets_to_env):

    copy_assets_to_env('assets_import_images_single_dir')

    with session_real() as session:
        count = session.query(ImageMetadata).count()
        assert count == 0

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 2

        path = os.path.join(Env.IMAGES_PATH, 'everything/dir_1')
        for f in os.listdir(path):
            new_f = os.path.splitext(f)
            new_f = f'{new_f[0]}_new{new_f[1]}'
            shutil.copy(os.path.join(path, f), os.path.join(path, new_f))

        importer = ImageMetadataImporter()
        importer.import_metadata(Env.IMAGES_PATH)

        count = session.query(ImageMetadata).count()
        assert count == 4