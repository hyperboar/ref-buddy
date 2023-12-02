from flask import Blueprint, render_template, jsonify, url_for
from sqlalchemy import func

from models.models_lump import Session, ImageMetadata

routes_discover = Blueprint('routes_discover', __name__)

@routes_discover.route('/discover')
def main_feed():
    return render_template('tpl_discover.html')

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

    return jsonify(response)