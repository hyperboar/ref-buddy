from flask import Blueprint, request, abort, render_template_string, render_template, redirect, jsonify
from markupsafe import Markup

from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Tag, Session, ImageMetadata

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
def add_image_tag():
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
def add_folder_tag():
    pass

@routes_tags.route('/get-image-tags')
def get_image_tags():
    args = request.args
    image_ids = [int(img) for img in args.get('image-id', default=[]).split(',')] # [int]

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