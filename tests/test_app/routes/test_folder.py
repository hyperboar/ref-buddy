import pytest

from tests.test_app.fixtures.data import add_4_images_1_path, clean_database



@pytest.fixture(scope='module', autouse=True)
def setup_database(config_path_testing_fresh_mod):
    pass

@pytest.fixture(autouse=True)
def reset_database(setup_database):
    clean_database()

@pytest.fixture(autouse=True)
def add_images_for_each_test(reset_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.mark.asyncio
async def test_export_urls(client):
    resp = await client.get('/export-urls')
    assert resp.status_code == 200

    json = await resp.json
    assert len(json) == 4

    assert 'id' in json[0]
    assert 'url' in json[0]