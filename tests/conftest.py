import glob
import os
import shutil
import uuid

import pytest

from shared_utils.Env import Env, ENV_DEFAULT
from tests import config_tmp_factory

@pytest.fixture(scope="session", autouse=True)
def verify_test_environment():
    assert os.environ.get("APP_ENV") == 'test', 'Tests should run with environment variable APP_ENV=test'

@pytest.fixture(scope="session", autouse=True)
def cleanup_db_files(config_path_testing_ok):
    """Remove test db before running any tests."""
    Env.apply_config(config_path_testing_ok)
    if os.path.exists(Env.DB_FILE):
        os.remove(Env.DB_FILE)

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    print('\n\nCleaning up files on session finished.')
    to_skip = ['.keep']

    to_remove = []
    to_remove += glob.glob('tests/test_app/assets/*.db')
    to_remove += glob.glob('tests/test_app/assets_tmp/*')
    to_remove += glob.glob('tests/config/testing_tmp_[!_]*.env')

    [os.path.normpath(p) for p in to_skip]
    [os.path.normpath(p) for p in to_remove]
    [to_remove.remove(item) for item in to_skip if item in to_remove]

    for file in to_remove:
        try:
            print(file)
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)
        except Exception as e:
            print(f'Could not remove {file}: {e}')


@pytest.fixture(scope='session')
def config_path_default():
    return ENV_DEFAULT

@pytest.fixture(scope='session')
def config_path_testing_ok():
    return './tests/config/testing.env'

@pytest.fixture
def config_path_testing_fresh_func():
    source = './tests/config/testing_tmp__.env'
    marker = str(uuid.uuid4())
    new_source = source.replace('__', '_' + marker)
    config_tmp_factory(source, new_source, marker)
    Env.apply_config(new_source)

    yield new_source

    os.remove(new_source)

@pytest.fixture(scope='module')
def config_path_testing_fresh_mod():
    source = './tests/config/testing_tmp__.env'
    marker = str(uuid.uuid4())
    new_source = source.replace('__', '_' + marker)
    config_tmp_factory(source, new_source, marker)
    Env.apply_config(new_source)

    yield new_source

    os.remove(new_source)