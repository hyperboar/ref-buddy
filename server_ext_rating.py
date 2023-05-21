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
