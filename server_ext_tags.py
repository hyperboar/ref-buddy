from flask import Blueprint, request, abort, render_template_string, render_template, redirect, jsonify, url_for

from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Tag, Session, ImageMetadata, TagSet
from server_args_helpers import get_current_paging, Args, get_arg
from server_widget_helpers import get_paging_widget, get_tags_editor, get_tags_filter

routes_tags = Blueprint('routes_tags', __name__)


@routes_tags.route('/tagged')
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

    tags_available = Ctrl.get_all_tags(sort_by_name=True, session=session)
    tags_filter = get_tags_filter(tags_available, session=session)
    paging = get_paging_widget(page)
    tags_editor = get_tags_editor(tags_available, session=session)

    out = render_template('tpl_view_folder.html', title='Tags', images=images, overview=overview, panel=tags_filter, paging=paging, tags_editor=tags_editor)
    session.close()
    return out

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
    _ , tags = get_arg(request.args, Args.tags)
    image_ids = get_arg(request.args, Args.mult_image_ids)

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')

    r = Ctrl.remove_image_tags(image_ids, tags)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string(str(r))
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

# ---- CRUD TAG ----

@routes_tags.route('/tags')
def show_tags():
    session = Session()
    tags = session.query(Tag).all()
    tags.sort(key=lambda t: t.tag)
    return render_template('crud/tpl_tags_list.html', tags=tags)

@routes_tags.route('/tags/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        session = Session()
        tag = request.form['tag']
        new_tag = Tag(tag=tag)
        session.add(new_tag)
        session.commit()
        return redirect('/tags')
    return render_template('crud/tpl_tags_add.html')

@routes_tags.route('/tags/edit/<int:tag_id>', methods=['GET', 'POST'])
def edit_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    if request.method == 'POST':
        new_tag = request.form['tag']
        tag.tag = new_tag
        session.commit()
        return redirect('/tags')
    return render_template('crud/tpl_tags_edit.html', tag=tag)

@routes_tags.route('/tags/delete/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    session.delete(tag)
    session.commit()
    return redirect('/tags')

# ---- END CRUD TAG ----

# ---- CRUD TAG SET ----

@routes_tags.route('/tag-sets')
def list_tag_sets():
    session = Session()
    tag_sets = session.query(TagSet).all()
    return render_template('crud/tpl_tagsets_list.html', tag_sets=tag_sets)


@routes_tags.route('/tag_sets/<int:tag_set_id>/edit', methods=['GET', 'POST'])
def tag_set_edit(tag_set_id):
    session = Session()
    tag_set = session.get(TagSet, tag_set_id)
    if not tag_set:
        return redirect(url_for('routes_tags.list_tag_sets'))

    if request.method == 'POST':
        tag_set.set_name  = request.form['set_name']
        tag_set.set_alias = request.form['set_alias']
        tag_set.tag_list  = request.form['tag_list']
        session.commit()
        return redirect(url_for('routes_tags.list_tag_sets', tag_set_id=tag_set.id))

    return render_template('crud/tpl_tagset_edit.html', tag_set=tag_set)

# ---- END CRUD TAG SET ----