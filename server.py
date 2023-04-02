import sqlite3

from flask import Flask, render_template_string, request, send_file, abort, send_from_directory, render_template
from image_metadata import ImageMetadata
from image_metadata_overview import ImageMetadataOverview
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
def favs():
    db = sqlite3.connect(Env.DB_FILE)
    images = ImageMetadata.get_favs(db)
    return render_template('tpl_favs.html', images=images)

@app.route('/last')
def last():
    db = sqlite3.connect(Env.DB_FILE)
    images = ImageMetadata.get_last(db)
    return render_template('tpl_last.html', images=images)

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

# @app.route('/random_image/<facing>/<timer>')
# def show_random_image(facing, timer):
#     db = sqlite3.connect(DB_FILE)
#     metadata = ImageMetadata.get_random_by_facing(db, facing)
#     if metadata is None:
#         return f'Error: No images found with facing "{facing}"'
#     return render_template_string(metadata.to_html(timer))

# @app.route('/random_image/<facing>')
# def show_random_image_deault_time(facing):
#     db = sqlite3.connect(DB_FILE)
#     f_num = ImageMetadata.str_to_facing(facing)
#     metadata = ImageMetadata.get_random_by_facing(db, f_num)
#     if metadata is None:
#         return f'Error: No images found with facing "{f_num}"'
#     return render_template_string(metadata.to_html(60))

# @app.route('/update_image/<int:image_id>', methods=['POST'])
# def update_image(image_id):
#     db = sqlite3.connect(DB_FILE)
#     metadata = ImageMetadata.get_by_id(db, image_id)
#     if metadata is None:
#         return f'Error: Image not found with ID "{image_id}"'
#
#     metadata.usage_count += 1
#     metadata.time_watching += 10  # Increase by 10 seconds for demo purposes
#     metadata.last_viewed = datetime.now()
#     metadata.save()
#
#     return f'Updated image: {metadata.path}'

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
    return render_template_string(metadata.to_html(60))

@app.route('/study-random')
def study_random():
    args = request.args
    study_type = int(args.get('source-type'))
    same_folder = int(args.get('same-folder') == "true")
    prev_image_id = int(args.get('image-id'))
    difficulty = int(args.get('difficulty'))
    facing = args.get('facing')
    timer = int(args.get('time-planned'))

    f_num = ImageMetadata.str_to_facing(facing)

    db = sqlite3.connect(Env.DB_FILE)
    metadata = ImageMetadata.get_random_by_study_type(db, study_type, same_folder, prev_image_id)
    if metadata is None:
        return f'Error: No images found with facing "{facing}"'

    return render_template_string(metadata.to_html(timer))

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
