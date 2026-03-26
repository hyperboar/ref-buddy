import json
import os

import pytest

from app.routes.tags_ai import EXPORTED_URLS_FILENAME
from shared_utils.env import Env
from tests.test_app.fixtures.data import clean_database, add_4_images_1_path, assign_ai_tag


@pytest.fixture(scope='module', autouse=True)
def setup_database(config_path_testing_fresh_mod):
    pass

@pytest.fixture(autouse=True)
def reset_database(setup_database):
    clean_database()

@pytest.fixture
def add_images_for_each_test(reset_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.fixture
def add_images_url_with_one_ai_tag(reset_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    assign_ai_tag(session)
    session.close()

@pytest.mark.asyncio
async def test_begin_works(client, add_images_url_with_one_ai_tag):
    resp = await client.get('/tags-ai/begin')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_save_exported_urls_valid(client, add_images_url_with_one_ai_tag):
    payload = {
        'json_urls':
            [
                {'id': 1, 'url': '/image/1'}
            ]
    }
    resp = await client.post('/tags-ai/save-exported-urls', json=payload)
    assert resp.status_code == 200

    path = os.path.join(Env.TMP_PATH, EXPORTED_URLS_FILENAME)
    assert os.path.exists(path)

    with open(path, 'r') as f:
        data = json.load(f)
        assert data['json_urls'][0]['id'] == payload['json_urls'][0]['id']

@pytest.mark.asyncio
async def test_save_exported_urls_invalid_empty(client, add_images_url_with_one_ai_tag):
    resp = await client.post('/tags-ai/save-exported-urls')
    assert resp.status_code != 200

    payload = {}
    resp = await client.post('/tags-ai/save-exported-urls', json=payload)
    assert resp.status_code != 200

    payload = {'json_urls': []}
    resp = await client.post('/tags-ai/save-exported-urls', json=payload)
    assert resp.status_code != 200