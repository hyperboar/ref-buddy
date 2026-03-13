import os
import pytest

from shared_utils.Env import Env


@pytest.fixture(scope="session", autouse=True)
def verify_test_environment():
    assert os.environ.get("APP_ENV") == 'test', 'Tests should run with environment variable APP_ENV=test'

@pytest.fixture(scope="session", autouse=True)
def cleanup_db_files():
    if os.path.exists(Env.DB_FILE):
        os.remove(Env.DB_FILE)

    # yield
    # someday, when I learn how to make sqlalchemy to let go of session, engine and eventually db file,
    # I'll remove the dam file!
    # Until then... oh well...