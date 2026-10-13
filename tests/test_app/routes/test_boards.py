import pytest

from app.models.models_lump import BoardImage
from tests.fixtures.data import add_4_images_1_path, clean_database, add_2_boards


@pytest.fixture(scope='module', autouse=True)
def setup_database(config_path_testing_fresh_mod):
    pass

@pytest.fixture(autouse=True)
def reset_database(setup_database):
    clean_database()

@pytest.fixture
def add_boards(reset_database, session_real):
    session = session_real()
    add_2_boards(session)
    session.close()

@pytest.fixture
def add_board_with_image(reset_database, session_real):
    session = session_real()
    add_4_images_1_path(session)
    add_2_boards(session)
    session.add(BoardImage(board_id=2, image_id=1))
    session.commit()
    session.close()

# @routes_board.route('/set-board-image-transform')
# @routes_board.route('/board-images/<int:b_id>')
# @routes_board.route('/board/add', methods=['POST'])
# @routes_board.route('/board/<int:b_id>')
# @routes_board.route('/boards')

@pytest.mark.asyncio
async def test_boards_all(client, add_boards):
    resp = await client.get('/boards')
    assert resp.status_code == 200

    # json = await resp.json
    # assert len(json) == 4
    #
    # assert 'id' in json[0]
    # assert 'url' in json[0]

@pytest.mark.asyncio
async def test_get_existing_board(client, add_boards):
    resp = await client.get('/board/1')
    assert resp.status_code == 200

    # json = await resp.json
    # assert len(json) == 3
    #
    # json = await resp.json
    # ids = [item['id'] for item in json]
    # assert 1 not in ids

@pytest.mark.asyncio
async def test_get_board_images(client, add_board_with_image):
    resp = await client.get('/board-images/1')
    assert resp.status_code == 200

    json = await resp.json
    print(json)
    assert len(json['images']) == 0, 'Empty board should not have images'

    resp = await client.get('/board-images/2')
    assert resp.status_code == 200

    json = await resp.json
    print(json)
    assert len(json['images']) > 0, 'Board should have images'
    # assert len(json) == 3
    #
    # json = await resp.json
    # ids = [item['id'] for item in json]
    # assert 1 not in ids

@pytest.mark.asyncio
async def test_widget_get_all_boards(client, add_boards):
    resp = await client.get('/widget/get-boards-all')
    assert resp.status_code == 200

    # json = await resp.json
    # assert len(json) == 3
    #
    # json = await resp.json
    # ids = [item['id'] for item in json]
    # assert 1 not in ids

