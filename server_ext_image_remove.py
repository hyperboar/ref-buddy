import os

from flask import Blueprint, jsonify, request, abort, render_template

from Env import Env
from maintenance import make_database_backup, cleanup_paths
from models.models_lump import Session, ImageMetadata, BoardImage, Discover, ImageColor, ImageExtra, ImageTag
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
def remove_permanent():
    if request.method != 'POST':
        return abort(404, 'Should be POST')
    session = Session()

    json = request.get_json()
    image_ids = json['image_ids']

    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.image_id.in_(image_ids))
              .filter(ImageMetadata.removed == 1)
              .all())

    if len(images) > 0:
        make_database_backup('before_perm_remove')

    count = 0
    for im in images:
        try:
            paths = [im.path_abs, os.path.join(Env.THUMB_PATH, str(im.image_id) + '.jpg')]
            if im.source_type_id == 3:  # video
                paths.append(im.path_abs[:-4])
            [os.remove(p) for p in paths if os.path.exists(p)]

            count += len([session.delete(item) for item in session.query(BoardImage).filter(BoardImage.image_id == im.image_id)])
            count += len([session.delete(item) for item in session.query(Discover).filter(Discover.image_id == im.image_id)])
            count += len([session.delete(item) for item in session.query(ImageColor).filter(ImageColor.image_id == im.image_id)])
            count += len([session.delete(item) for item in session.query(ImageExtra).filter(ImageExtra.image_id == im.image_id)])
            count += len([session.delete(item) for item in session.query(ImageTag).filter(ImageTag.image_id == im.image_id)])
            session.delete(im)
            count += 1
            session.flush()
        except Exception as e:
            print(e)
            raise e

    session.commit()

    cleanup_paths(session)

    session.close()

    return jsonify({'msg': 'ok', 'count': count})