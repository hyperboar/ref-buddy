import pytest
from quart.testing import QuartClient

from app.models import get_engine
from app.models.database_util import DatabaseUtil

from app import app_quart


@pytest.fixture
def client() -> QuartClient:
    return app_quart.test_client()

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    DatabaseUtil.drop_and_create(get_engine())