import pytest

from tests.test_app.fixtures.data import clean_database, add_4_images_1_path, add_2_tags

@pytest.fixture(scope="module", autouse=True)
def setup_module(config_path_testing_fresh_mod, copy_assets_to_env_mod):
    pass

@pytest.fixture(autouse=True)
def reset_database(setup_module, session_real):
    clean_database()
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.mark.asyncio
async def test_add_remove_image_tag(client):
    payload = {
        'image_ids': [1],
        'tags': ['tagme']
    }
    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

    resp = await client.post('/remove-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

@pytest.mark.asyncio
async def test_add_to_non_existent_single_image(client):
    payload = {
        'image_ids': [999],
        'tags': ['tagme']
    }
    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 404

    resp = await client.post('/remove-image-tags', json=payload)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_add_to_non_existent_mult_image(client):
    payload = {
        'image_ids': [999, 998],
        'tags': ['tagme']
    }
    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 404

    resp = await client.post('/remove-image-tags', json=payload)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_double_add(client):
    payload = {
        'image_ids': [1],
        'tags': ['tagme']
    }
    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

@pytest.mark.asyncio
async def test_double_remove(client):
    payload = {
        'image_ids': [1],
        'tags': ['tagme']
    }
    resp = await client.post('/add-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

    resp = await client.post('/remove-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 1

    resp = await client.post('/remove-image-tags', json=payload)
    assert resp.status_code == 200
    json = await resp.json
    assert json['count'] == 0