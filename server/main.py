import os.path

from flask import Flask, request, render_template
from flask_caching import Cache

from Env import Env
from image_metadata_controller import ImageMetadataController as ImageMetadataCtrl
from image_metadata_overview import ImageMetadataOverview
from maintenance import make_database_backup
from models.models_lump import Session, ImageColor, ImageMetadata
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

config = {
    # "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    'THUMB_STATIC': Env.THUMB_PATH
}

template_dir = os.path.join('..', 'templates')
static_dir = os.path.join('..', 'static')

app = Flask(__name__, static_url_path='/static', static_folder=static_dir, template_folder=template_dir)
app.config.from_mapping(config)

cache = Cache(app)

app.register_blueprint(routes_image)
app.register_blueprint(routes_image_remove)
app.register_blueprint(routes_folder)
app.register_blueprint(routes_rating)
app.register_blueprint(routes_tags)
app.register_blueprint(routes_dupes)
app.register_blueprint(routes_board)
app.register_blueprint(routes_discover)
app.register_blueprint(routes_misc)

@app.before_request
def before_request():
    make_database_backup()

@app.route('/')
def index():
    args = request.args
    hidden = int(args.get('hidden', default='0')) != 0

    images = ImageMetadataOverview.get_overview(hidden)
    return render_template('tpl_view_index.html', images=images)

@app.route('/favs')
def view_favs():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = ImageMetadataCtrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_favs(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = get_paging_widget(page)

    return render_template('tpl_view_folder.html', title='Favorites', paging=paging, images=images, overview=None)

@app.route('/latest_study')
def view_last():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = ImageMetadataCtrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_last(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = get_paging_widget(page)

    return render_template('tpl_view_folder.html', title='Latest study', paging=paging, images=images, overview=None)

@app.route('/palettes')
def view_image_colors():
    session = Session()

    sub = session.query(ImageColor.image_id).group_by(ImageColor.image_id).subquery()
    images = session.query(ImageMetadata).join(sub, ImageMetadata.image_id == sub.c.image_id).all()
    out = render_template('tpl_view_palettes.html', images=images)
    return out


if __name__ == '__main__':
    # db = sqlite3.connect(Env.DB_FILE)
    # ImageMetadataCtrl.static_initialize(db)

    app.run(host='0.0.0.0', port=Env.SERVER_PORT)
