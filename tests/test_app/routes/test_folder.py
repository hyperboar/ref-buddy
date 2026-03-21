import pytest

from tests.test_app.fixtures.data import add_4_images_1_path, clean_database, assign_ai_tag


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
async def test_export_urls(client, add_images_for_each_test):
    resp = await client.get('/export-urls')
    assert resp.status_code == 200

    json = await resp.json
    assert len(json) == 4

    assert 'id' in json[0]
    assert 'url' in json[0]

@pytest.mark.asyncio
async def test_export_urls_no_ai_tags_by_default(client, add_images_url_with_one_ai_tag):
    resp = await client.get('/export-urls')
    assert resp.status_code == 200

    json = await resp.json
    assert len(json) == 3

    json = await resp.json
    ids = [item['id'] for item in json]
    assert 1 not in ids