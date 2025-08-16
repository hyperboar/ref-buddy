import json
import os
from datetime import datetime

from flask import Blueprint, request, abort, render_template_string, render_template, jsonify
from models.models_lump import Session, ImageMetadata, Path
from models.view_filter_mapper import ViewFilterMapper
from server_args_helpers import get_current_paging, get_arg, Args
from image_metadata_controller import ImageMetadataController as Ctrl
from server_widget_helpers import get_paging_widget

routes_folder = Blueprint('routes_folder', __name__)

@routes_folder.route('/all')
def view_tags():

    mapper = ViewFilterMapper()
    params = mapper.request_to_filter_multiple_dto(request)

    session = Session()
    response, images = Ctrl.get_all_by_tags_new3(params, session=session)

    overview = {}
    overview["study_type"] = ', '.join(params.tags_pos_names)
    if len(params.tags_neg) > 0:
        overview["study_type"] += ' exclude:' + ', '.join(params.tags_neg_names)
    overview["path"] = ""

    paging = get_paging_widget(params.page)

    out = render_template('tpl_view_folder.html', title='All', images=json_for_folder_view(images, session), overview=overview, paging=paging)
    session.close()
    return out

@routes_folder.route('/folder/<int:path_id>')
def view_folder(path_id):

    mapper = ViewFilterMapper()
    params = mapper.request_to_filter_multiple_dto(request)

    params.path_id = path_id

    # rating = get_arg(request.args, Args.min_rating)
    # tags_pos, tags_neg = get_arg(request.args, Args.tags)
    # tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    # tags_pos, tags_neg = Ctrl.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    study_type, path, images = Ctrl.get_all_by_path_id2(params, session=session)
    if len(images) == 0:
        overview = None
    else:
        overview = images[0]
        overview.path_dir = os.path.dirname(overview.path_abs)



    paging = get_paging_widget(params.page)

    out = render_template('tpl_view_folder.html', title='Folder', d_sort='filename', images=json_for_folder_view(images, session), overview=overview, paging=paging)
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

@routes_folder.route('/export-urls/')
def export_urls():
    params = Ctrl.get_default_query_params()

    page, offset, limit = get_current_paging(request.args)
    params['page'] = page
    params['offset'] = offset
    params['limit'] = limit
    params['no_ai_tags'] = int(request.args.get('no_ai_tags', default='1'))
    params['min_rating'] = get_arg(request.args, Args.min_rating)
    params['max_rating'] = get_arg(request.args, Args.max_rating)
    params['tag_set'] = get_arg(request.args, Args.tag_set)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)

    session = Session()
    tags_pos, tags_neg = Ctrl.get_tags_by_set(params['tag_set'], tags_pos, tags_neg, session=session)
    tags_pos_names = Ctrl.get_tag_names(tags_pos, session=session)
    tags_neg_names = Ctrl.get_tag_names(tags_neg, session=session)
    params['tags_pos'] = tags_pos
    params['tags_neg'] = tags_neg
    params['tags_pos_names'] = tags_pos_names
    params['tags_neg_names'] = tags_neg_names

    response, images = Ctrl.get_all_by_tags_new2(params, session=session)

    out = [{"id": img.image_id, "url": f"/image/{ img.image_id }"} for img in images]

    session.close()
    return jsonify(out)