import os

from shared_utils.env import Env


def test_env_default_exist(config_path_default):
    assert os.path.exists(config_path_default)

def test_env_testing_template_exist(config_path_testing_fresh_func):
    assert os.path.exists(config_path_testing_fresh_func)

def test_env_applied(config_path_default, config_path_testing_fresh_func):
    Env.apply_config(config_path_default)
    db_path = Env.DB_FILE
    Env.apply_config(config_path_testing_fresh_func)
    db_path_test = Env.DB_FILE

    assert db_path != db_path_test
