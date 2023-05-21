import sqlite3

from flask import Blueprint, request, abort, render_template_string

from Env import Env
from image_metadata import ImageMetadata


routes_rating = Blueprint('routes_rating', __name__)


@routes_rating.route('/add-image-rating')
def add_image_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    db = sqlite3.connect(Env.DB_FILE)
    r = ImageMetadata.add_image_rating(db, image_id, rating)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))


@routes_rating.route('/add-folder-rating')
def add_folder_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    db = sqlite3.connect(Env.DB_FILE)

    img = ImageMetadata.get_by_id(db, image_id)
    imgs = ImageMetadata.get_all_by_path_id(db, img.path_id)[2]
    res = 0
    for i in imgs:
        res += ImageMetadata.add_image_rating(db, i.image_id, rating, auto_commit=False)

    if res > 0:
        abort(404, 'Something went wrong, fav not set, probably...')
        db.rollback()
        return

    db.commit()
    return 'ok'
