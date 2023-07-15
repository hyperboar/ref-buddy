from flask import Blueprint, request, abort, render_template_string
from models.models_lump import Session, ImageMetadata, Path

routes_folder = Blueprint('routes_folder', __name__)

@routes_folder.route('/folder-ord-add')
def add_folder_ord():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.ord += rating
    s.commit()

    return render_template_string(str('ok'))


@routes_folder.route('/set-folder-cover')
def set_folder_cover():
    args = request.args
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.preview = image_id
    s.commit()

    return render_template_string(str('ok'))


@routes_folder.route('/toggle-folder-hide')
def toggle_folder_hide():
    args = request.args
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.hidden = (path.hidden + 1) % 2
    s.commit()

    return render_template_string(str('ok'))