import glob
import os
import shutil
import uuid

from app.models import DatabaseEnvironment
from shared_utils.env import Env
from shared_utils.generators import create_required_folders

os.environ['APP_ENV'] = 'test'

def config_tmp_factory(source:str) -> (str, str):
    marker = str(uuid.uuid4())
    new_source = (source
                  .replace('__', '_' + marker)
                  .replace('./tests/config/', './tests/tmp/'))
    with open(source, 'r') as f:
        with open(new_source, 'w') as new_f:
            lines = []
            while line := f.readline():
                lines.append(line.replace('__', marker))
            new_f.writelines(lines)
    return new_source, marker

def init_new_env_config_template(template:str) -> (str, str):
    new_source, marker = config_tmp_factory(template)
    Env.apply_config(new_source)
    create_required_folders()
    DatabaseEnvironment.update_db_connection(True)
    return new_source, marker

def cleanup_tmp_files():
    to_skip = ['.keep']

    to_remove = []
    to_remove += glob.glob('tests/tmp/*')

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