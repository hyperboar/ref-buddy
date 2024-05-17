from datetime import datetime

from flask import Blueprint, render_template, jsonify, url_for, render_template_string
from sqlalchemy import func

from models.models_lump import Session, ImageMetadata, Discover

routes_discover = Blueprint('routes_discover', __name__)

@routes_discover.route('/discover')
def main_feed():
    return render_template('tpl_discover.html')

@routes_discover.route('/discover-last-active/<int:image_id>/')
def ping_image(image_id):
    session = Session()
    d = session.get(Discover, image_id)
    if d is None:
        session.add(Discover(image_id=image_id))
    else:
        d.last_active = datetime.now()

    session.commit()
    session.close()

    return render_template_string('ok')

@routes_discover.route('/discover-get-content/<int:count>/')
def get_content(count:int):
    response = []

    session = Session()

    q = session.query(ImageMetadata).filter(ImageMetadata.lost == 0)

    images = q.order_by(func.random()).limit(count).all()
    for im in images:
        response.append({
            'image_id': im.image_id,
            'image_url': f'/image/{im.image_id}',
            'image_study_url': url_for('routes_image.study_image', image_id=im.image_id),
            'rating': im.rating,
            'tags': [t.tag.tag for t in im.tags]
        })
    session.close()
    return jsonify(response)

@routes_discover.route('/discover-get-old-content/<int:count>/<int:image_id>/')
def get_old_content(count:int, image_id):
    session = Session()

    startId = session.get(Discover, image_id)
    if startId is None:
        timestamp = datetime.now()
    else:
        timestamp = startId.last_active

    ds = session.query(Discover).filter(Discover.last_active < timestamp).order_by(Discover.last_active.desc()).limit(count).all()

    response = []
    for d in ds:
        im = d.image
        if im.lost != 0:
            continue
        response.append({
            'image_id': im.image_id,
            'image_url': f'/image/{im.image_id}',
            'image_study_url': url_for('routes_image.study_image', image_id=im.image_id),
            'rating': im.rating,
            'tags': [t.tag.tag for t in im.tags]
        })
    session.close()
    return jsonify(response)