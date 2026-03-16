import pytest

from tests.test_app.fixtures.data import clean_database


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    clean_database()

@pytest.mark.asyncio
async def test_are_we_online(client):
    resp = await client.get('/')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_overview(client):
    resp = await client.get('/json/overview')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_favs(client):
    resp = await client.get('/favs')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_latest_study(client):
    resp = await client.get('/latest_study')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_palettes(client):
    resp = await client.get('/palettes')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_all(client):
    resp = await client.get('/all')
    assert resp.status_code == 200