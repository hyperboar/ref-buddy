import sqlite3

from flask import Flask, render_template_string, request, send_file
from image_metadata import ImageMetadata
import os
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the values of DB_PATH and DB_NAME from the environment
DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))
IMAGES_PATH = os.getenv('IMAGES_PATH')

app = Flask(__name__, static_url_path='/static')

@app.route('/image/<path:path>')
def show_image(path):
    db = sqlite3.connect(DB_FILE)
    metadata = ImageMetadata.get_by_path(db, path)
    if metadata is None:
        return f'Error: Image not found: {path}'
    return render_template_string(metadata.to_html())

@app.route('/random_image/<facing>/<timer>')
def show_random_image(facing, timer):
    db = sqlite3.connect(DB_FILE)
    metadata = ImageMetadata.get_random_by_facing(db, facing)
    if metadata is None:
        return f'Error: No images found with facing "{facing}"'
    return render_template_string(metadata.to_html(timer))

@app.route('/random_image/<facing>')
def show_random_image_deault_time(facing):
    db = sqlite3.connect(DB_FILE)
    f_num = ImageMetadata.str_to_facing(facing)
    metadata = ImageMetadata.get_random_by_facing(db, f_num)
    if metadata is None:
        return f'Error: No images found with facing "{f_num}"'
    return render_template_string(metadata.to_html(60))

@app.route('/update_image/<int:image_id>', methods=['POST'])
def update_image(image_id):
    db = sqlite3.connect(DB_FILE)
    metadata = ImageMetadata.get_by_id(db, image_id)
    if metadata is None:
        return f'Error: Image not found with ID "{image_id}"'

    metadata.usage_count += 1
    metadata.time_watching += 10  # Increase by 10 seconds for demo purposes
    metadata.last_viewed = datetime.now()
    metadata.save()

    return f'Updated image: {metadata.path}'

@app.route('/image/<int:image_id>')
def serve_image(image_id):
    print(f"getting id {image_id}")
    db = sqlite3.connect(DB_FILE)
    metadata = ImageMetadata.get_by_id(db, image_id)
    ext = os.path.splitext(metadata.path)[1]
    return send_file(os.path.join(IMAGES_PATH, metadata.path), mimetype=f'image/{ext}')

@app.route('/study-image/<int:image_id>')
def study_image(image_id):
    db = sqlite3.connect(DB_FILE)
    metadata =  ImageMetadata.get_by_id(db, image_id)
    if metadata is None:
        return f'Error: No images found with id "{image_id}"'
    return render_template_string(metadata.to_html(60))

@app.route('/study-random')
def study_random():
    args = request.args
    study_type = args.get('source-type')
    same_folder = int(args.get('same-folder') == "true")
    prev_image_id = int(args.get('image-id'))
    difficulty = int(args.get('difficulty'))
    facing = args.get('facing')
    timer = int(args.get('time-planned'))

    f_num = ImageMetadata.str_to_facing(facing)
    st_num = ImageMetadata.str_to_study_type(study_type)

    db = sqlite3.connect(DB_FILE)
    metadata = ImageMetadata.get_random_by_study_type(db, st_num, same_folder, prev_image_id)
    if metadata is None:
        return f'Error: No images found with facing "{facing}"'

    return render_template_string(metadata.to_html(timer))


if __name__ == '__main__':
    app.run(port=7071)
