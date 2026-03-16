import pytest

from tests.test_app.fixtures.data import add_4_images_1_path


@pytest.fixture(scope="module", autouse=True)
def add_images_for_all_tests(setup_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    session.close()

@pytest.mark.asyncio
async def test_image_get_html(client):
    resp = await client.get('/study-image/1')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_image_file(client):
    resp = await client.get('/image/1')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_data(client):
    resp = await client.get('/image-info/1')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_thumb(client):
    resp = await client.get('/thumb/1.jpg')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_palette(client):
    resp = await client.get('/color/palette/1')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_color_at_coord(client):
    resp = await client.get('/color-at-coord/1/0.0/0.0')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_next_image_data(client):
    resp = await client.get('/next-image/_/1')
    assert resp.status_code == 404

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
async def test_image_mark_last_study(client):
    resp = await client.get('/set-image-last-viewed/1')
    assert resp.status_code == 200

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