import os

from app import DatabaseEnvironment
from shared_utils.generators import create_new_db, create_required_folders
from shared_utils.env import Env

def test_new_db_created(config_path_testing_fresh_func):
    DatabaseEnvironment.update_db_connection(True)
    create_new_db()
    assert os.path.exists(Env.DB_FILE)

def test_folders_created(config_path_testing_fresh_func):
    create_required_folders()
    assert os.path.exists(Env.DB_PATH)
    assert os.path.exists(Env.DB_BACKUP_PATH)
    assert os.path.exists(Env.THUMB_PATH)
    assert os.path.exists(Env.TMP_PATH)