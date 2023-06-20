from flask import Blueprint, request, abort, render_template_string, render_template, redirect, jsonify
from markupsafe import Markup

from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Tag, Session, ImageMetadata
from server_args_helpers import get_current_paging, Args, get_arg
from server_widget_helpers import get_paging_widget

routes_tags = Blueprint('routes_tags', __name__)


@routes_tags.route('/tagged')
def view_tags():
    tags_pos, tags_neg = get_arg(request.args, Args.tags)

    tags_pos_ids = Ctrl.get_tags_by_names(tags_pos)
    tags_neg_ids = Ctrl.get_tags_by_names(tags_neg)

    page, offset, limit = get_current_paging(request.args)

    response, images = Ctrl.get_all_by_tags(tags_pos_ids, tags_neg_ids, limit, offset)

    overview = {}
    overview["study_type"] = ', '.join(tags_pos)
    if len(tags_neg) > 0:
        overview["study_type"] += ' exclude:' + ', '.join(tags_neg)
    overview["path"] = ""

    tags_available = Ctrl.get_all_tags(sort_by_name=True)
    panel = Markup(render_template('tpl_widget_tags_panel.html', tags=tags_available))
    paging = get_paging_widget(page)

    return render_template('tpl_view_folder.html', title='Tags', images=images, overview=overview, panel=panel, paging=paging, tags=tags_available)

@routes_tags.route('/add-image-tags')
def add_image_tag():
    tags, _ = get_arg(request.args, Args.tags)
    image_ids = get_arg(request.args, Args.mult_image_ids)

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')

    r = Ctrl.add_image_tags(image_ids, tags)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))

@routes_tags.route('/remove-image-tags')
def remove_image_tag():
    pass

@routes_tags.route('/add-folder-tags')
def add_folder_tag():
    pass

@routes_tags.route('/remove-folder-tags')
def remove_folder_tag():
    pass

@routes_tags.route('/get-image-tags')
def get_image_tags():
    image_ids = get_arg(request.args, Args.mult_image_ids)

    session = Session()
    data = {img.image_id: [t.tag.tag for t in img.tags] for img in session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(image_ids)).all()}

    for key in data:
        data[key].sort()

    if not data:
        abort(404, 'Something went wrong, fav not set, probably...')
    return jsonify(data)

# ---- CRUD ----

@routes_tags.route('/tags')
def show_tags():
    session = Session()
    tags = session.query(Tag).all()
    tags.sort(key=lambda t: t.tag)
    return render_template('tpl_tags_list.html', tags=tags)

@routes_tags.route('/tags/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        session = Session()
        tag = request.form['tag']
        new_tag = Tag(tag=tag)
        session.add(new_tag)
        session.commit()
        return redirect('/tags')
    return render_template('tpl_tags_add.html')

@routes_tags.route('/tags/edit/<int:tag_id>', methods=['GET', 'POST'])
def edit_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    if request.method == 'POST':
        new_tag = request.form['tag']
        tag.tag = new_tag
        session.commit()
        return redirect('/tags')
    return render_template('tpl_tags_edit.html', tag=tag)

@routes_tags.route('/tags/delete/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    session.delete(tag)
    session.commit()
    return redirect('/tags')

# ---- END CRUD ----