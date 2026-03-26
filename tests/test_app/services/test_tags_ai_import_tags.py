import datetime
import json
import os

import pytest
from pydantic import ValidationError

from app.models.models_lump import TagAi
from app.services.tags_ai import suck_folder_in, AI_TAGS_DIRNAME
from shared_utils.env import Env
from tests.test_app.fixtures.data import clean_database, add_4_images_1_path, assign_ai_tag


@pytest.fixture
def reset_database_with_assets_func(config_path_testing_fresh_func, copy_assets_to_env_func):
    clean_database()

@pytest.fixture
def add_images_for_each_test(session_real):
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.fixture
def add_images_url_with_one_ai_tag(session_real):
    session = session_real()
    add_4_images_1_path(session)
    assign_ai_tag(session)
    session.close()

@pytest.fixture
def ai_tags_payload_save_helper():
    def helper(payload, time_offset=0):
        path = os.path.join(Env.TMP_PATH, AI_TAGS_DIRNAME,
                            f'result_{datetime.datetime.now(tz=datetime.timezone.utc).timestamp() + time_offset}.json')
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(payload, f)
    return helper


def test_import_ai_tags_add_newtag_and_import(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 1,
                "timestamp": 1774526954.65208,
                "tags": {"0": 99,}
            }
        ]
    }
    ai_tags_payload_save_helper(payload)

    with session_real() as session:
        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
        assert existing_tag is None

        result = suck_folder_in(session)
        assert result == 1

        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
        assert existing_tag is not None

def test_import_ai_tags_add_one_newtag_and_mult_import(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 1,
                "timestamp": 1774526954.65208,
                "tags": {"0": 99,}
            },
            {
                "id": 2,
                "timestamp": 1774526954.65208,
                "tags": {"0": 80, }
            },
            {
                "id": 3,
                "timestamp": 1774526954.65208,
                "tags": {"0": 70, }
            }
        ]
    }
    ai_tags_payload_save_helper(payload)

    with session_real() as session:
        result = suck_folder_in(session)
        assert result == 3

def test_import_ai_tags_empty_images(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload = {
        "tags": ["tag_ai_1"]
    }
    ai_tags_payload_save_helper(payload)

    with session_real() as session:
        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
        assert existing_tag is None

        with pytest.raises(ValidationError):
            suck_folder_in(session)

            existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
            assert existing_tag is None

def test_import_ai_tags_no_files(reset_database_with_assets_func, session_real):
    with session_real() as session:
        result = suck_folder_in(session)
        assert result == 0

def test_import_ai_tags_mult_files(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload1 = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 1,
                "timestamp": 1774526954.65208,
                "tags": {
                    "0": 99,
                }
            }
        ]
    }
    payload2 = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 2,
                "timestamp": 1774526954.65208,
                "tags": {"0": 70,}
            }
        ]
    }
    ai_tags_payload_save_helper(payload1, 0)
    ai_tags_payload_save_helper(payload2, 100)

    with session_real() as session:
        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
        assert existing_tag is None

        result = suck_folder_in(session)
        assert result == 2

        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").first()
        assert existing_tag is not None

def test_import_ai_tags_newtag_imported_once(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload1 = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 1,
                "timestamp": 1774526954.65208,
                "tags": {"0": 99,}
            }
        ]
    }
    payload2 = {
        "tags": ["tag_ai_1"],
        "images": [
            {
                "id": 2,
                "timestamp": 1774526954.65208,
                "tags": {"0": 70,}
            }
        ]
    }
    ai_tags_payload_save_helper(payload1, 0)
    ai_tags_payload_save_helper(payload2, 100)

    with session_real() as session:
        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").all()
        assert existing_tag == []

        suck_folder_in(session)

        existing_tag = session.query(TagAi).filter(TagAi.tag == "tag_ai_1").all()
        assert len(existing_tag) == 1

def test_import_ai_tags_unused_tags_not_imported(reset_database_with_assets_func, add_images_for_each_test, session_real, ai_tags_payload_save_helper):
    payload1 = {
        "tags": ["tag_ai_1", "tag_ai_2"],
        "images": [
            {
                "id": 1,
                "timestamp": 1774526954.65208,
                "tags": {"0": 99,}
            }
        ]
    }
    ai_tags_payload_save_helper(payload1)

    with session_real() as session:
        existing_tag = session.query(TagAi).all()
        assert existing_tag == []

        suck_folder_in(session)

        existing_tag = session.query(TagAi).all()
        assert len(existing_tag) == 1
        assert existing_tag[0].tag == "tag_ai_1"