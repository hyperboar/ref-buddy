import pytest
from quart.testing import QuartClient

from app.models import Session

from app import app_quart


@pytest.fixture
def client() -> QuartClient:
    return app_quart.test_client()

@pytest.fixture(scope="module")
def session_real():
    return Session