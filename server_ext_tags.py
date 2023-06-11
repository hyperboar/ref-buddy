from flask import Blueprint, request, abort, render_template_string
from image_metadata_controller import ImageMetadataController


routes_tags = Blueprint('routes_tags', __name__)


@routes_tags.route('/add-image-tags')
def add_image_rating():
    args = request.args
    tags = args.get('tags', default=[]).split(',') # [str]
    image_ids = [int(img) for img in args.get('image-id', default=[]).split(',')] # [int]

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')

    r = ImageMetadataController.add_image_tags(image_ids, tags)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))


@routes_tags.route('/add-folder-tags')
def add_folder_rating():
    pass
