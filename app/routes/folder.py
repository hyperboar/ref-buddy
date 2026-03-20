import os

from quart import Blueprint, request, render_template_string, render_template, jsonify

from app.common.folder_dtos import FolderExportDto, FilterRequestDto
from app.models import Session
from app.models.models_lump import ImageMetadata
from app.services.image_metadata_controller import ImageMetadataController as Ctrl
from app.services.server_widget_helpers import get_paging_widget
from app.services.tags import get_tags_by_set, get_tag_names
from app.utils.misc import json_for_folder_view

routes_folder = Blueprint('routes_folder', __name__)


@routes_folder.route('/all')
async def view_tags():
    filter_dto = FilterRequestDto.model_validate(request.args.to_dict())

    with Session() as session:
        response, images = Ctrl.get_all_by_tags_new4(filter_dto, session=session)

        tags_pos_ids, tags_neg_ids = get_tags_by_set(filter_dto.tag_set, session, filter_dto.tags.pos,
                                                     filter_dto.tags.neg)
        tags_pos_names = get_tag_names(tags_pos_ids, session)
        tags_neg_names = get_tag_names(tags_neg_ids, session)

        overview = {}
        overview["category"] = ', '.join(tags_pos_names)
        if len(tags_neg_names) > 0:
            overview["category"] += ' exclude:' + ', '.join(tags_neg_names)
        overview["path"] = ""

        paging = await get_paging_widget(filter_dto.page)

        out = await render_template('tpl_view_folder.html', title='All', images=json_for_folder_view(images), overview=overview, paging=paging)
        session.close()
        return out

@routes_folder.route('/folder/<int:path_id>')
async def view_folder(path_id):
    data = request.args.to_dict()
    data['path-id'] = path_id
    filter_dto = FilterRequestDto.model_validate(data)

    with Session() as session:
        category, path, images = Ctrl.get_all_by_path_id2(filter_dto, session=session)
        if len(images) == 0:
            overview = None
        else:
            overview = images[0]
            overview.path_dir = os.path.dirname(overview.path_abs)

        paging = await get_paging_widget(filter_dto.page)
        return await render_template('tpl_view_folder.html', title='Folder', d_sort='filename', images=json_for_folder_view(images), overview=overview, paging=paging)

@routes_folder.route('/folder-ord-add')
async def add_folder_ord():
    args = request.args
    rating = int(args.get('rating', default='0'))
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.ord += rating
    s.commit()

    return await render_template_string(str('ok'))


@routes_folder.route('/set-folder-cover')
async def set_folder_cover():
    args = request.args
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.preview = image_id
    s.commit()

    return await render_template_string(str('ok'))


@routes_folder.route('/toggle-folder-hide')
async def toggle_folder_hide():
    args = request.args
    image_id = int(args.get('image-id'))

    s = Session()
    path = s.get(ImageMetadata, image_id).path_ref
    path.hidden = (path.hidden + 1) % 2
    s.commit()

    return await render_template_string(str('ok'))

@routes_folder.route('/export-urls')
async def export_urls():
    filter_dto = FilterRequestDto.model_validate(request.args.to_dict())

    with Session() as session:
        response, images = Ctrl.get_all_by_tags_new4(filter_dto, session)
        out = [FolderExportDto.model_validate(img) for img in images]
        return jsonify(out)