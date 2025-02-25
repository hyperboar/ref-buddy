from flask import Blueprint, request, abort, render_template_string, render_template, redirect, jsonify, url_for

from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Tag, Session, ImageMetadata, TagSet, Path, PathTag, Color
from server_args_helpers import Args, get_arg

routes_tags = Blueprint('routes_tags', __name__)


@routes_tags.route('/embed-panel-tag-filter')
def embed_panel_tag_filter():
    return render_template('tpl_widget_tags_filter_panel.html')

@routes_tags.route('/embed-panel-tag-editor')
def embed_panel_tag_editor():
    return render_template('tpl_widget_tags_editor_panel.html')

@routes_tags.route('/add-image-tags', methods=['POST'])
def add_image_tag():
    if request.method != 'POST':
        return abort(404, 'Should be POST')

    json = request.get_json()
    image_ids = json['image_ids']
    tags = json['tags']

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')
    session = Session()
    r = Ctrl.add_image_tags(image_ids, tags, session)
    session.close()
    if r is None:
        abort(404, 'Something went wrong...')
    return jsonify({'count': r})

@routes_tags.route('/remove-image-tags', methods=['POST'])
def remove_image_tag():
    if request.method != 'POST':
        return abort(404, 'Should be POST')

    json = request.get_json()
    image_ids = json['image_ids']
    tags = json['tags']

    if tags is [] or image_ids is []:
        abort(404, 'Empty tags or image ids')

    session = Session()
    r = Ctrl.remove_image_tags(image_ids, tags, session)
    session.close()
    if r is None:
        abort(404, 'Something went wrong...')
    return jsonify({'count': r})

@routes_tags.route('/add-folder-tags')
def add_folder_tag():
    pass

@routes_tags.route('/remove-folder-tags')
def remove_folder_tag():
    pass

#region ---- JSON API ----

@routes_tags.route('/tags/all')
def get_all_tags():
    session = Session()
    tags = session.query(Tag).all()
    out = {'colors': {}, 'tags': []}
    for tag in tags:
        out['tags'].append({'id': tag.id, 'name': tag.tag, 'c': tag.color_id})
        out['colors'][tag.color_id] = tag.color.hex
    session.close()
    return jsonify(out)

@routes_tags.route('/tags/image/single/<int:image_id>')
def image_tags_single(image_id):
    session = Session()
    im = session.get(ImageMetadata, image_id)
    tags = [{'color': it.tag.color.hex, 'name': it.tag.tag, 'ai': it.by_ai} for it in im.tags]
    out = [{'image_id': image_id, 'tags': tags}]
    session.close()
    return jsonify(out)

@routes_tags.route('/tags/image/bulk', methods=['POST'])
def image_tags_bulk():
    if request.method != 'POST':
        return abort(404, 'Should be GET')

    json = request.get_json()
    image_ids = json['image_ids'] if 'image_ids' in json else []

    session = Session()
    data = {}
    for img in session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(image_ids)).all():
        data[img.image_id] = [t.tag.tag for t in img.tags]

    return jsonify(data)

@routes_tags.route('/tags/set-list')
def tag_set_list():
    session = Session()
    out = [{'alias': s.set_alias, 'name': s.set_name, 'tags': s.tag_list} for s in session.query(TagSet).order_by(TagSet.set_name).all()]
    session.close()
    return jsonify(out)

#endregion ---- JSON API ----


#region ---- CRUD TAG ----

@routes_tags.route('/tags')
def show_tags():
    session = Session()
    tags = session.query(Tag).order_by(Tag.color_id, Tag.tag).all()
    return render_template('crud/tpl_tags_list.html', tags=tags)

@routes_tags.route('/tags/add', methods=['GET', 'POST'])
def add_tag():
    if request.method != 'POST':
        session = Session()
        colors = session.query(Color).filter(Color.color_name.startswith('tag_')).order_by(Color.id).all()
        return render_template('crud/tpl_tags_add.html', colors=colors)

    session = Session()
    tag = request.form['tag'].strip()
    color_id = int(request.form['color'].strip())
    new_tag = Tag(tag=tag, color_id=color_id)
    session.add(new_tag)
    session.commit()
    return redirect('/tags')


@routes_tags.route('/tags/edit/<int:tag_id>', methods=['GET', 'POST'])
def edit_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)

    if request.method != 'POST':
        session = Session()
        tag = session.get(Tag, tag_id)
        colors = session.query(Color).filter(Color.color_name.startswith('tag_')).order_by(Color.id).all()
        return render_template('crud/tpl_tags_edit.html', tag=tag, colors=colors)

    tag.tag = request.form['tag'].strip()
    tag.color_id = int(request.form['color'].strip())
    session.commit()
    return redirect('/tags')


@routes_tags.route('/tags/delete/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    session.delete(tag)
    session.commit()
    return redirect('/tags')

#endregion ---- CRUD TAG ----

#region ---- CRUD TAG SET ----

@routes_tags.route('/tag-sets')
def list_tag_sets():
    session = Session()
    tag_sets = session.query(TagSet).order_by(TagSet.set_name).all()
    return render_template('crud/tpl_tagsets_list.html', tag_sets=tag_sets)

@routes_tags.route('/tag-sets/add', methods=['GET', 'POST'])
def tag_set_add():
    session = Session()

    if request.method == 'POST':
        tag_set = TagSet()
        tag_set.set_name  = request.form['set_name'].strip()
        tag_set.set_alias = request.form['set_alias'].strip()
        tag_list_pos  = [t.strip() for t in request.form['tag_list_pos'].split(',')]
        tag_list_neg  = [t.strip() for t in request.form['tag_list_neg'].split(',')]
        tag_set.tag_list = tag_set.names_to_tag_list(tag_list_pos, tag_list_neg)
        session.add(tag_set)
        session.commit()
        return redirect(url_for('routes_tags.list_tag_sets'))

    tags = session.query(Tag).order_by(Tag.color_id, Tag.tag).all()

    out = render_template('crud/tpl_tagset_add.html', tags=tags)
    return out

@routes_tags.route('/tag-sets/<int:tag_set_id>/edit', methods=['GET', 'POST'])
def tag_set_edit(tag_set_id):
    session = Session()
    tag_set = session.get(TagSet, tag_set_id)
    if not tag_set:
        return redirect(url_for('routes_tags.list_tag_sets'))

    if request.method == 'POST':
        tag_set.set_name  = request.form['set_name'].strip()
        tag_set.set_alias = request.form['set_alias'].strip()
        tag_list_pos  = [t.strip() for t in request.form['tag_list_pos'].split(',')]
        tag_list_neg  = [t.strip() for t in request.form['tag_list_neg'].split(',')]
        tag_set.tag_list = tag_set.names_to_tag_list(tag_list_pos, tag_list_neg)
        session.commit()

    tags = session.query(Tag).order_by(Tag.color_id, Tag.tag).all()

    out = render_template('crud/tpl_tagset_edit.html', tag_set=tag_set, tags=tags)
    return out

#endregion ---- CRUD TAG SET ----

#region ---- CRUD PATH TAG ----

@routes_tags.route('/path-tags')
def list_path_tags():
    session = Session()
    paths = session.query(Path).order_by(Path.path_raw).all()

    return render_template('crud/tpl_path_tags.html', paths=paths)

@routes_tags.route('/path-tag/<int:path_id>/<tags_str>', methods=['GET'])
def path_tag_edit(path_id, tags_str:str):
    if not path_id:
        return abort(404, 'Path id or tags list is not set')

    remote_tags_str = [t.strip().lower() for t in tags_str.split(',')]

    session = Session()

    new_tags = session.query(Tag).filter(Tag.tag.in_(remote_tags_str)).all()

    path = session.get(Path, path_id)
    tags = [pt.tag for pt in path.tags]


    tags_to_add    = [t.id for t in new_tags if t not in tags]
    tags_to_remove = [t.id for t in tags     if t not in new_tags]

    for t in tags_to_add:
        session.merge(PathTag(path_id=path_id, tag_id=t))

    remove_tags = session.query(PathTag).filter(PathTag.path_id == path_id, PathTag.tag_id.in_(tags_to_remove)).all()
    for t in remove_tags:
        session.delete(t)

    session.commit()

    updated_tags = [t.tag.tag for t in path.tags]
    updated_tags.sort()
    out = jsonify({'tags': updated_tags})
    session.close()
    return out

#endregion ---- CRUD PATH TAG ----