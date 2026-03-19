import os.path
import shutil

import pytest

from shared_utils.env import Env


@pytest.fixture(scope='session')
def assets_path():
    return os.path.abspath('./tests/test_app/assets')

@pytest.fixture
def copy_assets_to_env_func(assets_path):
    dst = os.path.normpath(os.path.join(Env.IMAGES_PATH, '..'))
    shutil.copytree(assets_path, dst, dirs_exist_ok=True)

@pytest.fixture(scope='module')
def copy_assets_to_env_mod(assets_path):
    dst = os.path.normpath(os.path.join(Env.IMAGES_PATH, '..'))
    shutil.copytree(assets_path, dst, dirs_exist_ok=True)