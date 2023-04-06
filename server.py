import sqlite3

from flask import Flask, render_template_string, request, send_file, abort, send_from_directory, render_template
from image_metadata import ImageMetadata
from image_metadata_overview import ImageMetadataOverview, OverviewPath
import os
from datetime import datetime
from Env import Env


app = Flask(__name__, static_url_path='/static')
app.config['THUMB_STATIC'] = Env.THUMB_PATH

@app.route('/')
def index():
    db = sqlite3.connect(Env.DB_FILE)
    images = ImageMetadataOverview.get_overview(db)
    return render_template('tpl_index.html', images=images)

@app.route('/favs')
def view_favs():
    db = sqlite3.connect(Env.DB_FILE)
    images = ImageMetadata.get_favs(db)
    return render_template('tpl_favs.html', images=images)

@app.route('/last')
def view_last():
    db = sqlite3.connect(Env.DB_FILE)
    images = ImageMetadata.get_last(db)
    return render_template('tpl_last.html', images=images)

@app.route('/folder/<int:path_id>')
def view_folder(path_id):
    db = sqlite3.connect(Env.DB_FILE)
    study_type, path, images = ImageMetadata.get_all_by_path_id(db, path_id)
    overview = OverviewPath.from_image_metadata(images[0])

    return render_template('tpl_view_folder.html', images=images, overview=overview)

@app.route('/thumb/<path:path>')
def send_static_thumb(path):
    return send_from_directory(app.config['THUMB_STATIC'], path)

@app.route('/image/<path:path>')
def show_image(path):
    db = sqlite3.connect(Env.DB_FILE)
    metadata = ImageMetadata.get_by_path(db, path)
    if metadata is None:
        return f'Error: Image not found: {path}'
    return render_template_string(metadata.to_html())

@app.route('/image/<int:image_id>')
def serve_image(image_id):
    print(f"getting id {image_id}")
    db = sqlite3.connect(Env.DB_FILE)
    metadata = ImageMetadata.get_by_id(db, image_id)
    ext = os.path.splitext(metadata.path)[1]
    return send_file(os.path.join(Env.IMAGES_PATH, metadata.path), mimetype=f'image/{ext}')

@app.route('/study-image/<int:image_id>')
def study_image(image_id):
    db = sqlite3.connect(Env.DB_FILE)
    metadata = ImageMetadata.get_by_id(db, image_id)
    if metadata is None:
        abort(404, f'Error: No images found with id "{image_id}"')

    args = request.args
    match args.get('time-planned'):
        case None:
            timer = 60
        case s:
            timer = int(s)

    return render_template('tpl_image.html', image=metadata, timer=timer)

@app.route('/study-random')
def study_random():
    args = request.args
    study_type = int(args.get('source-type'))
    same_folder = int(args.get('same-folder') == "true")
    prev_image_id = int(args.get('image-id'))
    difficulty = int(args.get('difficulty'))
    facing = args.get('facing')

    match args.get('time-planned'):
        case None:
            timer = 120
        case s:
            timer = int(s)

    db = sqlite3.connect(Env.DB_FILE)
    metadata = ImageMetadata.get_random_by_study_type(db, study_type, same_folder, prev_image_id)
    if metadata is None:
        return f'Error: No images found with facing "{facing}"'

    return render_template('tpl_image.html', image=metadata, timer=timer)

@app.route('/set-image-fav')
def set_image_fav():
    args = request.args
    is_fav = int(args.get('is-fav'))
    image_id = int(args.get('image-id'))

    db = sqlite3.connect(Env.DB_FILE)
    r = ImageMetadata.set_image_fav(db, image_id, is_fav)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string('yep')

@app.route('/set-image-last-viewed')
def set_image_last_viewed():
    args = request.args
    image_id = int(args.get('image-id'))
    now = datetime.now()

    db = sqlite3.connect(Env.DB_FILE)
    r = ImageMetadata.set_image_last_viewed(db, image_id, now)

    if not r:
        abort(404, 'Something went wrong, last viewed not updated, probably...')
    return render_template_string('yep')


if __name__ == '__main__':
    db = sqlite3.connect(Env.DB_FILE)
    ImageMetadata.static_initialize(db)

    app.run(port=Env.SERVER_PORT)
