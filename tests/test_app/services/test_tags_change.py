import pytest

from app.services.image_metadata_controller import ImageMetadataController
from tests.fixtures.data import clean_database, add_4_images_1_path, add_2_tags


@pytest.fixture(scope='module', autouse=True)
def setup_database(config_path_testing_fresh_mod):
    pass

@pytest.fixture(autouse=True)
def add_images_and_tags_for_each_test(session_real):
    clean_database()
    with session_real() as session:
        add_4_images_1_path(session)
        add_2_tags(session)

image_tags_sets = [
    ([1], ['tagme']),
    ([1], ['tagme', 'pos_1']),
    ([1, 2], ['tagme']),
    ([1, 2], ['tagme', 'pos_1']),
]

@pytest.mark.parametrize("image_ids, tags", image_tags_sets)
def test_add_image_tags(session_real, image_ids, tags):
    with session_real() as session:
        res = ImageMetadataController.add_image_tags(image_ids, tags, session)
        assert res == len(image_ids) * len(tags)

        # for all images
        for idx in image_ids:
            im = ImageMetadataController.get_or_raise(session, idx)
            assert len(im.tags) == len(tags)

            # check all tags
            image_tags = [t.tag.tag for t in im.tags]
            for t in tags:
                assert t in image_tags

@pytest.mark.parametrize("tags, expected_tags", [
    (['tagme', 'tagme'], ['tagme']),
    (['tagme', 'pos_1', 'tagme', 'pos_1'], ['tagme', 'pos_1']),
])
def test_add_double_image_tags(session_real, tags, expected_tags):
    with session_real() as session:
        res = ImageMetadataController.add_image_tags([1], tags, session)
        assert res == len(expected_tags)

        im = ImageMetadataController.get_or_raise(session, 1)
        assert len(im.tags) == len(expected_tags)

        # check all tags
        image_tags = [t.tag.tag for t in im.tags]
        for t in expected_tags:
            assert t in image_tags

@pytest.mark.parametrize("image_ids, tags", image_tags_sets)
def test_remove_image_tags(session_real, image_ids, tags):
    with session_real() as session:
        # add
        ImageMetadataController.add_image_tags(image_ids, tags, session)
        # then remove
        res = ImageMetadataController.remove_image_tags(image_ids, tags, session)
        assert res == len(image_ids) * len(tags)

        # for all images
        for idx in image_ids:
            im = ImageMetadataController.get_or_raise(session, idx)
            assert len(im.tags) == 0

            # check all tags
            image_tags = [t.tag.tag for t in im.tags]
            for t in tags:
                assert t not in image_tags

@pytest.mark.parametrize("tags, expected_tags", [
    (['tagme', 'tagme'], ['tagme']),
    (['tagme', 'pos_1', 'tagme', 'pos_1'], ['tagme', 'pos_1']),
])
def test_remove_double_image_tags(session_real, tags, expected_tags):
    with session_real() as session:
        res = ImageMetadataController.add_image_tags([1], tags, session)
        assert res == len(expected_tags)

        im = ImageMetadataController.get_or_raise(session, 1)
        assert len(im.tags) == len(expected_tags)

        # check all tags
        image_tags = [t.tag.tag for t in im.tags]
        for t in expected_tags:
            assert t in image_tags

def test_remove_image_tags_not_exist(session_real):
    with session_real() as session:
        # add
        res = ImageMetadataController.remove_image_tags([1], ['tagme'], session)
        # then remove
        assert res == 0

        im = ImageMetadataController.get_or_raise(session, 1)
        assert len(im.tags) == 0