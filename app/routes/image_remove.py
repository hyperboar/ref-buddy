from quart import Blueprint, jsonify, request, abort, render_template

from app.common.folder_dtos import FilterRequestDto
from app.models import Session
from app.models.models_lump import ImageMetadata
from app.utils.misc import json_for_folder_view
from shared_utils.cleanup import cleanup_paths, remove_permanent
from app.services.image_metadata_controller import ImageMetadataController

routes_image_remove = Blueprint('routes_image_remove', __name__)

@routes_image_remove.route('/images/removed/all')
async def remove_all():
    with Session() as session:
        images = (session.query(ImageMetadata)
                  .filter(ImageMetadata.removed == 1)
                  .filter(ImageMetadata.lost == 0)
                  .order_by(ImageMetadata.imported_at.desc())
                  .all())

        extra = 'page-remove'
        return await render_template('tpl_view_folder.html', title='Removed images', d_sort='filename',
                              images=json_for_folder_view(images), overview='', extra=extra)


@routes_image_remove.route('/images/removed/filtered')
async def remove_filtered():
    data = request.args.to_dict()
    data['removed'] = '1'
    filter_dto = FilterRequestDto.model_validate(data)
    with Session() as session:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
        images = (q
                  .filter(ImageMetadata.removed == 1)
                  .filter(ImageMetadata.lost == 0)
                  .order_by(ImageMetadata.imported_at.desc())
                  .all())

        extra = 'page-remove'
        return await render_template('tpl_view_folder.html', title='Removed images', d_sort='filename',
                               images=json_for_folder_view(images), overview='', extra=extra)

@routes_image_remove.route('/remove/images', methods=['POST'])
async def remove_mult():
    with Session() as session:
        json = await request.get_json()
        image_ids = json['image_ids']

        images = (session.query(ImageMetadata)
                  .filter(ImageMetadata.image_id.in_(image_ids))
                  .filter(ImageMetadata.removed == 0)
                  .all())
        for im in images:
            im.mark_removed(session=session, auto_commit=False)

        session.commit()

        return jsonify({'msg': 'ok'})

@routes_image_remove.route('/remove/restore', methods=['POST'])
async def restore_mult():
    with Session() as session:
        json = await request.get_json()
        image_ids = json['image_ids']

        images = (session.query(ImageMetadata)
                  .filter(ImageMetadata.image_id.in_(image_ids))
                  .filter(ImageMetadata.removed == 1)
                  .all())
        for im in images:
            im.mark_restored(session=session, auto_commit=False)

        session.commit()

        return jsonify({'msg': 'ok'})

@routes_image_remove.route('/remove/permanent', methods=['POST'])
async def permanent_remove():
    with Session() as session:
        json = await request.get_json()
        image_ids = json['image_ids']

        count = remove_permanent(image_ids, session = session)
        cleanup_paths(session)
        return jsonify({'msg': 'ok', 'count': count})