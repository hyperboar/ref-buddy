from quart import Blueprint
from quart import request, render_template, jsonify
from app.services.image_metadata_controller import ImageMetadataController as ImageMetadataCtrl
from app.models.models_lump import Session, ImageColor, ImageMetadata
from app.services.server_args_helpers import get_arg, Args
from app.services.image_metadata_overview import ImageMetadataOverview
from app.services.server_widget_helpers import get_paging_widget
from app.services.tags import get_tags_by_set
from app.utils.misc import json_for_folder_view, get_current_paging

routes_root = Blueprint('routes_root', __name__)

@routes_root.route('/')
async def overview():
    args = request.args
    hidden = int(args.get('hidden', default='0')) != 0

    images = ImageMetadataOverview.get_overview(hidden)
    return await render_template('tpl_view_index.html', images=images)

@routes_root.route('/json/overview')
async def json_overview():
    args = request.args
    hidden = int(args.get('hidden', default='0')) != 0

    images = ImageMetadataOverview.get_overview(hidden)

    result = []
    for im in images:
        result.append({
            'id': im.image_id,
            'thumb': f'/thumb/{ im.image_id }.jpg',
            'path_link': f'/folder/{im.path_id}',
            'path_dir': im.path_dir,
            'type':im.category,
            'is_hidden': im.hidden,
            'study_first_link': f'/study-image/{ im.image_id }?same-folder=true&time-planned=120'
        })

    return jsonify(result)

@routes_root.route('/favs')
async def view_favs():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_favs(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = await get_paging_widget(page)

    return await render_template('tpl_view_folder.html', title='Favorites', paging=paging, images=images, overview=None)

@routes_root.route('/latest_study')
async def view_last():
    page, offset, limit = get_current_paging(request.args)
    rating = get_arg(request.args, Args.min_rating)
    tags_pos, tags_neg = get_arg(request.args, Args.tags)
    tag_set_id = get_arg(request.args, Args.tag_set)

    session = Session()
    tags_pos, tags_neg = get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

    images = ImageMetadataCtrl.get_last(start=offset, count=limit, tags=(tags_pos,tags_neg), min_rating=rating, session=session)
    images = json_for_folder_view(images)

    paging = await get_paging_widget(page)

    return await render_template('tpl_view_folder.html', title='Latest study', paging=paging, images=images, overview=None)

@routes_root.route('/palettes')
async def view_image_colors():
    session = Session()

    sub = session.query(ImageColor.image_id).group_by(ImageColor.image_id).subquery()
    images = session.query(ImageMetadata).join(sub, ImageMetadata.image_id == sub.c.image_id).all()
    out = await render_template('tpl_view_palettes.html', images=images)
    return out