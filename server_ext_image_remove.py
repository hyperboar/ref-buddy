from flask import Blueprint, jsonify, request, abort, render_template

from maintenance import remove_permanent
from models.models_lump import Session, ImageMetadata
from server_ext_folder import json_for_folder_view

routes_image_remove = Blueprint('routes_image_remove', __name__)

@routes_image_remove.route('/all/removed')
def remove_show():
    session = Session()
    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.removed == 1)
              .filter(ImageMetadata.lost == 0)
              .order_by(ImageMetadata.imported_at.desc())
              .all())

    extra = 'page-remove'
    out = render_template('tpl_view_folder.html', title='Removed images', d_sort='filename',
                          images=json_for_folder_view(images, session), overview='', extra=extra)
    session.close()
    return out

@routes_image_remove.route('/remove/images', methods=['POST'])
def remove_mult():
    if request.method != 'POST':
        return abort(404, 'Should be POST')
    session = Session()

    json = request.get_json()
    image_ids = json['image_ids']

    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.image_id.in_(image_ids))
              .filter(ImageMetadata.removed == 0)
              .all())
    for im in images:
        im.mark_removed(session=session, auto_commit=False)

    session.commit()
    session.close()

    return jsonify({'msg': 'ok'})

@routes_image_remove.route('/remove/restore', methods=['POST'])
def restore_mult():
    if request.method != 'POST':
        return abort(404, 'Should be POST')
    session = Session()

    json = request.get_json()
    image_ids = json['image_ids']

    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.image_id.in_(image_ids))
              .filter(ImageMetadata.removed == 1)
              .all())
    for im in images:
        im.mark_restored(session=session, auto_commit=False)

    session.commit()
    session.close()

    return jsonify({'msg': 'ok'})

@routes_image_remove.route('/remove/permanent', methods=['POST'])
def permanent_remove():
    if request.method != 'POST':
        return abort(404, 'Should be POST')
    session = Session()

    json = request.get_json()
    image_ids = json['image_ids']

    count = remove_permanent(image_ids, session = session)
    return jsonify({'msg': 'ok', 'count': count})

