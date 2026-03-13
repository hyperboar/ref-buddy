from typing import Annotated

from quart import Blueprint, request, abort, render_template_string
from app.services.image_metadata_controller import ImageMetadataController
from app.models import Session

from pydantic import BaseModel, Field, BeforeValidator

routes_rating = Blueprint('routes_rating', __name__)

class DtoImageRating(BaseModel):
    rating: Annotated[int, BeforeValidator(lambda v: v[0])] = Field(alias='r', default=0)
    image_ids: list[int] = Field(alias='image-ids', default='')

@routes_rating.route('/add-image-rating')
async def add_image_rating():
    data = request.args.to_dict(flat=False)
    dto = DtoImageRating.model_validate(data)

    try:
        r = ImageMetadataController.add_image_rating(image_id=dto.image_ids[0], rating_add=dto.rating)
    except Exception:
        abort(404, 'Something went wrong...')

    return await render_template_string(str(r))

@routes_rating.route('/add-mult-image-rating')
async def add_mult_image_rating():
    data = request.args.to_dict(flat=False)
    dto = DtoImageRating.model_validate(data)

    r = ImageMetadataController.add_mult_image_rating(image_ids=dto.image_ids, rating_add=dto.rating)
    if r < 0:
        abort(404, 'Something went wrong...')

    return await render_template_string(str(r))


@routes_rating.route('/add-folder-rating')
async def add_folder_rating():
    data = request.args.to_dict(flat=False)
    dto = DtoImageRating.model_validate(data)

    s = Session()
    img = ImageMetadataController.get_by_id(dto.image_ids[0], session=s)
    imgs = ImageMetadataController.get_all_by_path_id(img.path_id, session=s)[2]
    res = 0
    for i in imgs:
        res += ImageMetadataController.add_image_rating(image_id=i.image_id, rating_add=dto.rating, session=s)

    if res == 0:
        abort(404, 'Something went wrong, fav not set, probably...')

    return 'ok'

@routes_rating.route('/get-image-rating')
async def get_image_rating():
    data = request.args.to_dict(flat=False)
    dto = DtoImageRating.model_validate(data)

    r = ImageMetadataController.get_image_rating(dto.image_ids[0])
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')

    return await render_template_string(str(r))