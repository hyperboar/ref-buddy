from flask import Blueprint, request, abort, render_template_string
from image_metadata_controller import ImageMetadataController


routes_rating = Blueprint('routes_rating', __name__)


@routes_rating.route('/add-image-rating')
def add_image_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    r = ImageMetadataController.add_image_rating(image_id, rating)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))


@routes_rating.route('/add-folder-rating')
def add_folder_rating():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    img = ImageMetadataController.get_by_id(image_id)
    imgs = ImageMetadataController.get_all_by_path_id(img.path_id)[2]
    res = 0
    for i in imgs:
        res += ImageMetadataController.add_image_rating(i.image_id, rating)

    if res > 0:
        abort(404, 'Something went wrong, fav not set, probably...')
        # db.rollback()
        return

    # db.commit()
    return 'ok'
