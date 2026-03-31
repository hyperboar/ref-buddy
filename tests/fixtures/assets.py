import os
import shutil

from shared_utils.env import Env


def copy_assets_from_to_env(src:str):
    src = os.path.normpath(src)
    dst = os.path.normpath(os.path.join(Env.IMAGES_PATH, '..'))
    shutil.copytree(src, dst, dirs_exist_ok=True)