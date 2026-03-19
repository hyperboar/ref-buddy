import pytest
from quart.testing import QuartClient

from app.models import Session

from app import create_app
from shared_utils.env import Env


@pytest.fixture
def client() -> QuartClient:
    app_quart = create_app()
    app_quart.config['THUMB_STATIC'] = Env.THUMB_PATH
    return app_quart.test_client()

@pytest.fixture(scope="module")
def session_real():
    return Session