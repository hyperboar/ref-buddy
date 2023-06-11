from flask import Blueprint, request, abort, render_template_string, render_template
from markupsafe import Markup

from image_metadata_controller import ImageMetadataController as Ctrl


routes_tags = Blueprint('routes_tags', __name__)


@routes_tags.route('/tagged')
def view_tags():
    args = request.args
    tags_all = args.get('tags', default="").split(',')
    tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
    tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

    tags_pos = Ctrl.get_tags_by_names(tags_pos)
    tags_neg = Ctrl.get_tags_by_names(tags_neg)

    page_str = args.get('page', default='1')
    page = max(int(page_str) - 1, 0)

    limit = 100
    offset = limit * page
    response, images = Ctrl.get_all_by_tags(tags_pos, tags_neg, limit, offset)

    overview = {}
    overview["study_type"] = ', '.join(tags_all)
    overview["path"] = ""

    tags_available = Ctrl.get_all_tags(sort_by_name=True)
    panel = Markup(render_template('tpl_tags_panel.html', tags=tags_available))
    return render_template('tpl_view_folder.html', title='Tags', images=images, overview=overview, panel=panel, tags=tags_available)

@routes_tags.route('/add-image-tags')
def add_image_rating():
    args = request.args
    tags = args.get('tags', default=[]).split(',') # [str]
    image_ids = [int(img) for img in args.get('image-id', default=[]).split(',')] # [int]

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')

    r = Ctrl.add_image_tags(image_ids, tags)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))


@routes_tags.route('/add-folder-tags')
def add_folder_rating():
    pass
