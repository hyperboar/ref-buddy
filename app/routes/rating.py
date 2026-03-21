from typing import Annotated

from quart import Blueprint, request, jsonify

from app.common.dto_basic import IntResultResponse
from app.services.image_metadata_controller import ImageMetadataController
from app.models import Session

from pydantic import BaseModel, Field, BeforeValidator, model_validator, ValidationError

routes_rating = Blueprint('routes_rating', __name__)

class ImageRatingDto(BaseModel):
    rating: int = Field(alias='r', default=0)
    image_ids: Annotated[list[int], BeforeValidator(lambda v: [int(i) for i in v.split(',')])] = Field(alias='image-ids')

    @model_validator(mode='before')
    @classmethod
    def validate_args(cls, values):
        if 'image-ids' not in values:
            raise ValidationError('image-ids is empty')
        return values

@routes_rating.route('/add-image-rating')
async def add_image_rating():
    dto = ImageRatingDto.model_validate(request.args.to_dict())
    with Session() as session:
        r = ImageMetadataController.add_image_rating(image_id=dto.image_ids[0], rating_add=dto.rating, session=session)
        return jsonify(IntResultResponse.model_validate(r))

@routes_rating.route('/add-mult-image-rating')
async def add_mult_image_rating():
    dto = ImageRatingDto.model_validate(request.args.to_dict())

    session = Session()
    ImageMetadataController.all_exist_or_raise(session, dto.image_ids)
    r = ImageMetadataController.add_mult_image_rating(image_ids=dto.image_ids, rating_add=dto.rating, session=session)

    return jsonify(IntResultResponse.model_validate(r))


@routes_rating.route('/add-folder-rating')
async def add_folder_rating():
    dto = ImageRatingDto.model_validate(request.args.to_dict())

    with Session() as session:
        img = ImageMetadataController.get_or_raise(session, dto.image_ids[0])
        imgs = ImageMetadataController.get_all_by_path_id(img.path_id, session=session)
        image_ids = [im.image_id for im in imgs]
        ImageMetadataController.all_exist_or_raise(session, image_ids)
        r = ImageMetadataController.add_mult_image_rating(image_ids=image_ids, rating_add=dto.rating, session=session)

        return jsonify(IntResultResponse.model_validate(r))

@routes_rating.route('/get-image-rating')
async def get_image_rating():
    dto = ImageRatingDto.model_validate(request.args.to_dict())
    session = Session()
    r = ImageMetadataController.get_or_raise(session, dto.image_ids[0]).rating

    return jsonify(IntResultResponse.model_validate(r))