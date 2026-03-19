import pytest

from shared_utils.env import ENV_DEFAULT


@pytest.fixture(scope='session')
def config_path_default():
    return ENV_DEFAULT