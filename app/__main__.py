import os.path

import socketio
import uvicorn
from quart import Quart, request, render_template, jsonify
from flask_caching import Cache

# Moved server scripts to subdir. Env, maintenance and other scripts are now in PARENT directory, so...
import sys

sys.path.append(os.getcwd())

from shared_utils.Env import Env
from app.image_metadata_controller import ImageMetadataController as ImageMetadataCtrl
from app.image_metadata_overview import ImageMetadataOverview
from shared_utils.maintenance import make_database_backup
from app.models.models_lump import Session, ImageColor, ImageMetadata
from server_args_helpers import get_arg, get_current_paging, Args
from server_ext_board import routes_board
from server_ext_discover import routes_discover
from server_ext_dupes import routes_dupes
from server_ext_folder import routes_folder, json_for_folder_view
from server_ext_image_remove import routes_image_remove
from server_ext_misc import routes_misc
from server_ext_rating import routes_rating
from server_ext_single_image import routes_image
from server_ext_tags import routes_tags
from server_widget_helpers import get_paging_widget
from server_ext_tags_ai import routes_tags_ai

config = {
    # "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    'THUMB_STATIC': Env.THUMB_PATH
}

template_dir = os.path.join('templates')
static_dir = os.path.join('static')

app = Quart(__name__, static_url_path='/static', static_folder=static_dir, template_folder=template_dir)
app.config.from_mapping(config)

cache = Cache(app)

app.register_blueprint(routes_image)
app.register_blueprint(routes_image_remove)
app.register_blueprint(routes_folder)
app.register_blueprint(routes_rating)
app.register_blueprint(routes_tags)
app.register_blueprint(routes_tags_ai)
app.register_blueprint(routes_dupes)
app.register_blueprint(routes_board)
app.register_blueprint(routes_discover)
app.register_blueprint(routes_misc)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(sio, app)

@app.before_request
def before_request():
    make_database_backup()

@app.route('/')
async def overview():
    args = request.args
    hidden = int(args.get('hidden', default='0')) != 0

    images = ImageMetadataOverview.get_overview(hidden)
    return await render_template('tpl_view_index.html', images=images)

@app.route('/json/overview')
async def json_overview():
    args = request.args
    hidden = int(args.get('hidden', default='0')) != 0

    images = ImageMetadataOverview.get_overview(hidden)

    result = []
    for im in images:
        result.append({
            'id': im.image_id,
            'thumb': f'/thumb/{ im.image_id }.jpg',
            'path_link': f'/folder/{im.path_id}',
            'path_dir': im.path_dir,
            'type':im.study_type,
            'is_hidden': im.hidden,
            'study_first_link': f'/study-image/{ im.image_id }?same-folder=true&time-planned=120'
        })

    return jsonify(result)

@app.route('/favs')
async def view_favs():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = ImageMetadataCtrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_favs(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = await get_paging_widget(page)

    return await render_template('tpl_view_folder.html', title='Favorites', paging=paging, images=images, overview=None)

@app.route('/latest_study')
async def view_last():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = ImageMetadataCtrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_last(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = await get_paging_widget(page)

    return await render_template('tpl_view_folder.html', title='Latest study', paging=paging, images=images, overview=None)

@app.route('/palettes')
async def view_image_colors():
    session = Session()

    sub = session.query(ImageColor.image_id).group_by(ImageColor.image_id).subquery()
    images = session.query(ImageMetadata).join(sub, ImageMetadata.image_id == sub.c.image_id).all()
    out = await render_template('tpl_view_palettes.html', images=images)
    return out

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"Received message from {sid}: {data}")
    await sio.emit("response", f"Server got: {data}", to=sid)

@sio.event
async def join(sid, room):
    print(f"{sid} joined room: {room}")
    await sio.emit("response", f"{sid} joined room {room}", to=sid)

def run() -> None:
    # db = sqlite3.connect(Env.DB_FILE)
    # ImageMetadataCtrl.static_initialize(db)
    uvicorn.run('main:asgi_app', host='0.0.0.0', port=int(Env.SERVER_PORT), reload=True, lifespan="off")

if __name__ == '__main__':
    run()
