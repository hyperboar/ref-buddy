import os
from dotenv import load_dotenv

ENV_DEFAULT = './config/default.env'
ENV_USER = './config/user.env'

is_testing = os.environ.get('APP_ENV') == 'test'

class Env:
    DB_FILE:str
    DB_PATH:str
    DB_NAME:str

    DB_BACKUP_PATH:str
    DB_BACKUP_INTERVAL:int
    DB_BACKUP_MAX_COUNT:int

    IMAGES_PATH:str
    DRAWING_PATH:str
    THUMB_PATH:str
    TMP_PATH:str
    TMP_PATH_GIF:str
    THUMB_MAX_SIZE:int
    IMPORT_FORMATS:[str]

    SERVER_PORT:str
    DEFAULT_FPS_SPLIT:int
    DEFAULT_PER_PAGE_LIMIT:int
    DEFAULT_STUDY_TIMER:int
    LOGS:str

    VIDEO_PLAYER_PATH:str

    @classmethod
    def apply_config(cls, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(config_path, f'Env config file not found at {config_path}')

        load_dotenv(ENV_DEFAULT, override=True)
        if ENV_DEFAULT != config_path:
            load_dotenv(config_path, override=True)

        # database
        cls.DB_FILE = os.path.abspath(os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME')))
        cls.DB_PATH = os.path.abspath(os.getenv('DB_PATH'))
        cls.DB_NAME = os.getenv('DB_NAME')
        cls.DB_BACKUP_PATH = os.path.abspath(os.getenv('DB_BACKUP_PATH', default=os.getenv('DB_PATH')))
        # minutes. Happens only on app start
        cls.DB_BACKUP_INTERVAL = int(os.getenv('DB_BACKUP_INTERVAL_MIN'))
        cls.DB_BACKUP_MAX_COUNT = int(os.getenv('DB_BACKUP_MAX_COUNT'))

        # images
        cls.IMAGES_PATH = os.path.abspath(os.getenv('IMAGES_PATH'))
        cls.DRAWING_PATH = os.path.abspath(os.getenv('DRAWING_PATH'))
        cls.THUMB_PATH = os.path.abspath(os.getenv('THUMB_PATH'))
        cls.TMP_PATH = os.path.abspath(os.getenv('TMP_PATH'))
        cls.TMP_PATH_GIF = os.path.abspath(os.getenv('TMP_PATH_GIF'))
        cls.THUMB_MAX_SIZE = int(os.getenv('THUMB_MAX_SIZE'))
        cls.IMPORT_FORMATS = list(map(lambda f: '.' + f.strip(), os.getenv('IMPORT_FORMATS').split(',')))

        # other defaults
        cls.SERVER_PORT = os.getenv('SERVER_PORT')
        cls.DEFAULT_FPS_SPLIT = int(os.getenv('FPS_SPLIT'))
        cls.DEFAULT_PER_PAGE_LIMIT = int(os.getenv('PER_PAGE_LIMIT'))
        cls.DEFAULT_STUDY_TIMER = int(os.getenv('STUDY_TIMER'))

        cls.LOGS = os.getenv('LOGS')

        cls.VIDEO_PLAYER_PATH = os.getenv('VIDEO_PLAYER_PATH')

        # some additional setup
        os.environ['SQLITE_TMPDIR'] = cls.TMP_PATH

if not is_testing and os.path.exists(ENV_USER):
    Env.apply_config(ENV_USER)