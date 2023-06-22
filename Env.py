import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Env:
    # Get the values of DB_PATH and DB_NAME from the environment
    DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))
    IMAGES_PATH = os.getenv('IMAGES_PATH')
    SERVER_PORT = os.getenv('SERVER_PORT')
    THUMB_PATH = os.getenv('THUMB_PATH')
    THUMB_MAX_SIZE = int(os.getenv('THUMB_MAX_SIZE'))

    # defaults
    DEFAULT_FPS_SPLIT = int(os.getenv('FPS_SPLIT'))
    DEFAULT_PER_PAGE_LIMIT = int(os.getenv('PER_PAGE_LIMIT'))
    DEFAULT_STUDY_TIMER = int(os.getenv('STUDY_TIMER'))
