import os
import shutil

import pytest

from shared_utils.env import Env
from tests import cleanup_tmp_files, init_new_env_config_template


@pytest.fixture(scope="session", autouse=True)
def verify_test_environment():
    assert os.environ.get("APP_ENV") == 'test', 'Tests should run with environment variable APP_ENV=test'

@pytest.fixture(scope="session", autouse=True)
def session_start(verify_test_environment, config_path_testing_template):
    cleanup_tmp_files()
    # stub config just to warm up db at the start
    init_new_env_config_template(config_path_testing_template)

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    print('\n\nCleaning up files on session finished.')
    cleanup_tmp_files()

@pytest.fixture(scope='session')
def config_path_testing_template():
    return './tests/config/testing_tmp__.env'

@pytest.fixture
def config_path_testing_fresh_func(config_path_testing_template):
    source, marker = init_new_env_config_template(config_path_testing_template)
    return source

@pytest.fixture(scope='module')
def config_path_testing_fresh_mod(config_path_testing_template):
    source, marker = init_new_env_config_template(config_path_testing_template)
    return source

@pytest.fixture(scope='session')
def assets_template_path():
    return os.path.abspath('./tests/test_app/assets')

@pytest.fixture(scope='module')
def copy_assets_to_env_mod(assets_template_path):
    dst = os.path.normpath(os.path.join(Env.IMAGES_PATH, '..'))
    shutil.copytree(assets_template_path, dst, dirs_exist_ok=True)

@pytest.fixture
def copy_assets_to_env_func(assets_template_path):
    dst = os.path.normpath(os.path.join(Env.IMAGES_PATH, '..'))
    shutil.copytree(assets_template_path, dst, dirs_exist_ok=True)