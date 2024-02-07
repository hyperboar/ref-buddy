import json
import os
from datetime import datetime

from flask import Blueprint, request, abort, render_template_string, render_template
from models.models_lump import Session, ImageMetadata, Path
from server_args_helpers import get_current_paging, get_arg, Args
from image_metadata_controller import ImageMetadataController as Ctrl
from server_widget_helpers import get_paging_widget

routes_folder = Blueprint('routes_folder', __name__)

@routes_folder.route('/all')
def view_tags():
    page, offset, limit = get_current_paging(request.args)
    tag_set_id = get_arg(request.args, Args.tag_set)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)

    session = Session()
    tags_pos, tags_neg = Ctrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)
    tags_pos_names = Ctrl.get_tag_names(tags_pos, session=session)
    tags_neg_names = Ctrl.get_tag_names(tags_neg, session=session)

    response, images = Ctrl.get_all_by_tags(tags_pos, tags_neg, limit, offset, session=session)

    overview = {}
    overview["study_type"] = ', '.join(tags_pos_names)
    if len(tags_neg) > 0:
        overview["study_type"] += ' exclude:' + ', '.join(tags_neg_names)
    overview["path"] = ""

    paging = get_paging_widget(page)

    out = render_template('tpl_view_folder.html', title='All', images=json_for_folder_view(images, session), overview=overview, paging=paging)
    session.close()
    return out

@routes_folder.route('/folder/<int:path_id>')
def view_folder(path_id):
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = Ctrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    study_type, path, images = Ctrl.get_all_by_path_id(path_id, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    if len(images) == 0:
        overview = None
    else:
        overview = images[0]
        overview.path_dir = os.path.dirname(overview.path_abs)

    out = render_template('tpl_view_folder.html', title='Folder', d_sort='filename', images=json_for_folder_view(images, session), overview=overview)
    session.close()
    return out

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

def json_for_folder_view(images, session=None) -> str:
    data = {'images': []}
    for im in images:
        print(im.imported_at)
        data['images'].append({
            'id': im.image_id,
            'r': im.rating,
            'fn': im.filename,
            'i_at': datetime.timestamp(im.imported_at)*1000,
            'video': 1 if im.source_type_id == 2 or im.source_type_id == 3 else 0
        })

    return json.dumps(data)