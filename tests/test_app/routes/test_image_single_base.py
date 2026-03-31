import pytest

from tests.fixtures.data import add_4_images_1_path, clean_database


@pytest.fixture(scope="module", autouse=True)
def add_images_for_all_tests(config_path_testing_fresh_mod, copy_all_assets_to_env_mod, session_real):
    clean_database()
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.mark.parametrize('route', [
    '/study-image/1',
    '/image/1',
    '/image-info/1',
    '/thumb/1.jpg',
    '/color/palette/1',
    '/color-at-coord/1/0.0/0.0',
    '/set-image-last-viewed/1'
])
@pytest.mark.asyncio
async def test_image_ok(client, route):
    resp = await client.get(route)
    assert resp.status_code == 200

@pytest.mark.parametrize('route', [
    '/image/999',
    '/image-info/999',
    '/thumb/999.jpg',
    '/color/palette/999',
    '/color-at-coord/999/0.0/0.0',
    '/set-image-fav/999/0',
    '/set-image-last-viewed/999',
    '/next-image/_/1',
    '/next-image/_/999',
    '/next-image/fwd_id/999',
    '/next-image/bck_id/999',
    '/next-image/fwd_rnd/999',
    '/next-image/fwd_name/999',
    '/next-image/bck_name/999'
])
@pytest.mark.asyncio
async def test_image_not_exist(client, route):
    resp = await client.get(route)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_image_get_next_image_data(client):
    resp = await client.get('/next-image/fwd_id/1')
    assert resp.status_code == 200
    json = await resp.json
    assert json['id'] == 2

    resp = await client.get('/next-image/bck_id/2')
    assert resp.status_code == 200
    json = await resp.json
    assert json['id'] == 1

    resp = await client.get('/next-image/fwd_rnd/1')
    assert resp.status_code == 200
    json = await resp.json
    assert json['id'] != 1, 'Random image should not repeat current image'

    resp = await client.get('/next-image/fwd_name/3')
    assert resp.status_code == 200
    json = await resp.json
    assert json['id'] == 4

    resp = await client.get('/next-image/bck_name/4')
    assert resp.status_code == 200
    json = await resp.json
    assert json['id'] == 3

@pytest.mark.asyncio
async def test_image_fav(client):
    resp = await client.get('/image-info/1')
    json = await resp.json
    assert json['fav'] == 0

    # mark fav
    resp = await client.get('/set-image-fav/1/1')
    assert resp.status_code == 200
    resp = await client.get('/image-info/1')
    json = await resp.json
    assert json['fav'] == 1

    # unmark fav
    resp = await client.get('/set-image-fav/1/0')
    assert resp.status_code == 200
    resp = await client.get('/image-info/1')
    json = await resp.json
    assert json['fav'] == 0