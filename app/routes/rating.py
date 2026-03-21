from typing import Annotated

from quart import Blueprint, request, abort, render_template_string, jsonify

from app.common.dto_basic import EmptyResponse
from app.services.image_metadata_controller import ImageMetadataController
from app.models import Session

from pydantic import BaseModel, Field, BeforeValidator, model_validator

routes_rating = Blueprint('routes_rating', __name__)

class ImageRatingDto(BaseModel):
    rating: Annotated[int, BeforeValidator(lambda v: v[0])] = Field(alias='r', default=0)
    image_ids: Annotated[list[int], BeforeValidator(lambda v: [int(i) for i in v[0].split(',')])] = Field(alias='image-ids')

    @model_validator(mode='before')
    def validate_args(values):
        if 'image-ids' not in values:
            abort(404, 'No images ids')
        return values

@routes_rating.route('/add-image-rating')
async def add_image_rating():
    data = request.args.to_dict(flat=False)
    dto = ImageRatingDto.model_validate(data)
    with Session() as session:
        ImageMetadataController.add_image_rating(image_id=dto.image_ids[0], rating_add=dto.rating, session=session)
        return jsonify(EmptyResponse())

@routes_rating.route('/add-mult-image-rating')
async def add_mult_image_rating():
    data = request.args.to_dict(flat=False)
    dto = ImageRatingDto.model_validate(data)

    session = Session()
    ImageMetadataController.all_exist_or_raise(session, dto.image_ids)
    ImageMetadataController.add_mult_image_rating(image_ids=dto.image_ids, rating_add=dto.rating, session=session)

    return jsonify(EmptyResponse())


@routes_rating.route('/add-folder-rating')
async def add_folder_rating():
    data = request.args.to_dict(flat=False)
    dto = ImageRatingDto.model_validate(data)

    with Session() as session:
        img = ImageMetadataController.get_or_raise(session, dto.image_ids[0])
        imgs = ImageMetadataController.get_all_by_path_id(img.path_id, session=session)
        image_ids = [im.image_id for im in imgs]
        ImageMetadataController.all_exist_or_raise(session, image_ids)
        ImageMetadataController.add_mult_image_rating(image_ids=image_ids, rating_add=dto.rating, session=session)

        return jsonify(EmptyResponse())

@routes_rating.route('/get-image-rating')
async def get_image_rating():
    data = request.args.to_dict(flat=False)
    dto = ImageRatingDto.model_validate(data)
    session = Session()
    r = ImageMetadataController.get_or_raise(session, dto.image_ids[0]).rating

    return await render_template_string(str(r))