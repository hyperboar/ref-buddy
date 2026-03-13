import os.path

import socketio

from quart import Quart
from flask_caching import Cache

# Moved server scripts to subdir. Env, maintenance and other scripts are now in PARENT directory, so...
import sys

sys.path.append(os.getcwd())

from shared_utils.Env import Env
from shared_utils.maintenance import make_database_backup
from app.routes.root import routes_root
from app.routes.board import routes_board
from app.routes.discover import routes_discover
from app.routes.folder import routes_folder
from app.routes.image_remove import routes_image_remove
from app.routes.misc import routes_misc
from app.routes.rating import routes_rating
from app.routes.image_single import routes_image
from app.routes.tags import routes_tags
from app.routes.tags_ai import routes_tags_ai

from app.models import DatabaseEnvironment
from shared_utils.Env import is_testing

DatabaseEnvironment.update_db_connection(is_testing)

config = {
    # 'DEBUG': True,
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'THUMB_STATIC': Env.THUMB_PATH
}

template_dir = 'templates'
static_dir = 'static'

app_quart = Quart(__name__, static_url_path='/static', static_folder=static_dir, template_folder=template_dir)
app_quart.config.from_mapping(config)

cache = Cache(app_quart)

app_quart.register_blueprint(routes_root)
app_quart.register_blueprint(routes_image)
app_quart.register_blueprint(routes_image_remove)
app_quart.register_blueprint(routes_folder)
app_quart.register_blueprint(routes_rating)
app_quart.register_blueprint(routes_tags)
app_quart.register_blueprint(routes_tags_ai)
app_quart.register_blueprint(routes_board)
app_quart.register_blueprint(routes_discover)
app_quart.register_blueprint(routes_misc)

if not is_testing:
    app_quart.before_request(make_database_backup)



sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(sio, app_quart)