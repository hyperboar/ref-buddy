import os

import pytest

from app.models import Session
from tests.fixtures.assets import copy_assets_from_to_env
from tests.fixtures.data import clean_database


@pytest.fixture(scope="module")
def session_real():
    return Session

@pytest.fixture(autouse=True)
def reset_database(config_path_testing_fresh_func):
    clean_database()

@pytest.fixture
def copy_assets_to_env():
    def inner(src_path:str):
        src_path = os.path.join('./tests/fixtures/files', src_path)
        copy_assets_from_to_env(src_path)
    return inner

