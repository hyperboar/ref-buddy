import pytest

from tests.test_app.fixtures.data import add_4_images_1_path, clean_database


@pytest.fixture(autouse=True)
def setup_database():
    clean_database()

@pytest.fixture(autouse=True)
def add_images_for_each_test(setup_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    session.close()

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