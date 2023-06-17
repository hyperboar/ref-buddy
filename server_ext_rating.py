from flask import Blueprint, request, abort, render_template_string
from image_metadata_controller import ImageMetadataController
from models.models_lump import Session

routes_rating = Blueprint('routes_rating', __name__)


@routes_rating.route('/add-image-rating')
def add_image_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    r = ImageMetadataController.add_image_rating(image_id=image_id, rating_add=rating)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))

@routes_rating.route('/add-mult-image-rating')
def add_mult_image_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_ids = args.get('image-id', default='').split(',')

    r = ImageMetadataController.add_mult_image_rating(image_ids=image_ids, rating_add=rating)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))


@routes_rating.route('/add-folder-rating')
def add_folder_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    s = Session()
    img = ImageMetadataController.get_by_id(image_id, session=s)
    imgs = ImageMetadataController.get_all_by_path_id(img.path_id, session=s)[2]
    res = 0
    for i in imgs:
        res += ImageMetadataController.add_image_rating(image_id=i.image_id, rating_add=rating, session=s)

    if res == 0:
        abort(404, 'Something went wrong, fav not set, probably...')
        # db.rollback()
        return

    # db.commit()
    return 'ok'

@routes_rating.route('/get-image-rating')
def get_image_rating():
    args = request.args
    image_id = args.get('image-id', default='')

    r = ImageMetadataController.get_image_rating(image_id)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))