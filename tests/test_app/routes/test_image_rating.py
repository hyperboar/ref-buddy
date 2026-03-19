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

@pytest.mark.parametrize('route', [
    '/get-image-rating?image-ids=999',
    '/add-image-rating?image-ids=999&r=0',
    '/add-image-rating?image-ids=999&r=0',
    '/add-mult-image-rating?image-ids=999,998&r=1',
    '/add-folder-rating?image-ids=999&r=1'
])
@pytest.mark.asyncio
async def test_image_not_exist(client, route):
    resp = await client.get(route)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_image_get_single_rating(client):
    resp = await client.get('/get-image-rating?image-ids=1')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_image_change_single_rating(client):
    # no change
    resp = await client.get('/add-image-rating?image-ids=1&r=0')
    assert resp.status_code == 200
    resp = await client.get('/get-image-rating?image-ids=1')
    assert resp.status_code == 200
    text = await resp.data
    assert text == b'0'

    # +1
    resp = await client.get('/add-image-rating?image-ids=1&r=1')
    assert resp.status_code == 200
    resp = await client.get('/get-image-rating?image-ids=1')
    assert resp.status_code == 200
    text = await resp.data
    assert text == b'1'

    # +10
    resp = await client.get('/add-image-rating?image-ids=1&r=10')
    assert resp.status_code == 200
    resp = await client.get('/get-image-rating?image-ids=1')
    assert resp.status_code == 200
    text = await resp.data
    assert text == b'11'

    # -1, negative
    resp = await client.get('/add-image-rating?image-ids=2&r=-1')
    assert resp.status_code == 200
    resp = await client.get('/get-image-rating?image-ids=2')
    assert resp.status_code == 200
    text = await resp.data
    assert text == b'-1'

@pytest.mark.asyncio
async def test_image_change_mult_rating(client):
    # change 1
    resp = await client.get('/add-mult-image-rating?image-ids=1,2&r=1')
    assert resp.status_code == 200

    resp = await client.get('/get-image-rating?image-ids=1')
    text = await resp.data
    assert text == b'1'
    resp = await client.get('/get-image-rating?image-ids=2')
    text = await resp.data
    assert text == b'1'

    # change 2
    resp = await client.get('/add-mult-image-rating?image-ids=1&r=1')
    assert resp.status_code == 200

    resp = await client.get('/get-image-rating?image-ids=1')
    text = await resp.data
    assert text == b'2'
    resp = await client.get('/get-image-rating?image-ids=2')
    text = await resp.data
    assert text == b'1'

@pytest.mark.asyncio
async def test_image_change_folder_rating(client):
    resp = await client.get('/add-folder-rating?image-ids=1&r=1')
    assert resp.status_code == 200

    resp = await client.get('/get-image-rating?image-ids=1')
    text = await resp.data
    assert text == b'1'
    resp = await client.get('/get-image-rating?image-ids=2')
    text = await resp.data
    assert text == b'1'
    resp = await client.get('/get-image-rating?image-ids=3')
    text = await resp.data
    assert text == b'1'
    resp = await client.get('/get-image-rating?image-ids=4')
    text = await resp.data
    assert text == b'1'