import os
from dotenv import load_dotenv

ENV_DEFAULT = './config/default.env'
ENV_USER = './config/user.env'

# Load environment variables from default .env file
load_dotenv(ENV_DEFAULT)
# load environment overrides from user's .env file
if os.path.exists(ENV_USER):
    load_dotenv(ENV_USER, override=True)


class Env:
    # database
    DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))
    DB_PATH = os.getenv('DB_PATH')
    DB_NAME = os.getenv('DB_NAME')
    DB_BACKUP_PATH = os.getenv('DB_BACKUP_PATH', default=os.getenv('DB_PATH'))
    # minutes. Happens only on app start
    DB_BACKUP_INTERVAL = int(os.getenv('DB_BACKUP_INTERVAL_MIN'))
    DB_BACKUP_MAX_COUNT = int(os.getenv('DB_BACKUP_MAX_COUNT'))

    # images
    IMAGES_PATH = os.getenv('IMAGES_PATH')
    THUMB_PATH = os.getenv('THUMB_PATH')
    TMP_PATH = os.getenv('TMP_PATH')
    TMP_PATH_GIF = os.getenv('TMP_PATH_GIF')
    THUMB_MAX_SIZE = int(os.getenv('THUMB_MAX_SIZE'))
    IMPORT_FORMATS = list(map(lambda f: '.' + f.strip(), os.getenv('IMPORT_FORMATS').split(',')))

    # other defaults
    SERVER_PORT = os.getenv('SERVER_PORT')
    DEFAULT_FPS_SPLIT = int(os.getenv('FPS_SPLIT'))
    DEFAULT_PER_PAGE_LIMIT = int(os.getenv('PER_PAGE_LIMIT'))
    DEFAULT_STUDY_TIMER = int(os.getenv('STUDY_TIMER'))

    VIDEO_PLAYER_PATH = os.getenv('VIDEO_PLAYER_PATH')


