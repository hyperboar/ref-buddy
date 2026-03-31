import pytest

from tests.fixtures.data import add_4_images_1_path, add_1_mp4_1_path, add_1_gif_1_path, clean_database


@pytest.fixture(scope="module", autouse=True)
def setup_database(copy_all_assets_to_env_mod):
    clean_database()

@pytest.fixture(scope="module", autouse=True)
def add_images_for_all_tests(setup_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    add_1_mp4_1_path(session)
    add_1_gif_1_path(session)
    session.close()

@pytest.mark.parametrize('route', [
    '/video/999',
    '/anim-info/999',
    '/anim-frames-zip/999'
])
@pytest.mark.asyncio
async def test_video_anim_not_exist(client, route):
    resp = await client.get(route)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_image_get_html(client):
    # video
    resp = await client.get('/study-image/5')
    assert resp.status_code == 200

    # gif
    resp = await client.get('/study-image/6')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_image_file(client):
    resp = await client.get('/video/5') # source mp4
    assert resp.status_code == 200
    resp = await client.get('/image/5') # mp4 to gif
    assert resp.status_code == 200

    resp = await client.get('/image/6')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_data(client):
    resp = await client.get('/image-info/5')
    assert resp.status_code == 200
    json = await resp.json
    assert json['url_image'].startswith('/video')
    assert json['content_type'] == 3

    resp = await client.get('/image-info/6')
    assert resp.status_code == 200
    json = await resp.json
    assert json['content_type'] == 2

@pytest.mark.asyncio
async def test_image_get_thumb(client):
    resp = await client.get('/thumb/5.jpg')
    assert resp.status_code == 200

    resp = await client.get('/thumb/6.jpg')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_anim_frames(client):
    resp = await client.get('/anim-info/6')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_get_anim_frames(client):
    resp = await client.get('/anim-frames-zip/6')
    assert resp.status_code == 200