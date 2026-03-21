import json

from pydantic import BaseModel, Field, model_validator

from app.common.dto_basic import AttrModel


class ImageInfoDto(AttrModel):
    id:int = Field(alias='image_id')
    path_id:int
    path:str = Field(alias='path_abs')
    content_type:int = Field(alias='source_type_id')
    video:int = None
    fav:int
    rating:int
    extra:dict = None
    thumb:str = None
    url_image:str = None

    @model_validator(mode='before')
    @classmethod
    def generate_missing_fields(cls, im):
        im.extra = json.loads(im.extras[0].data if len(im.extras) > 0 else "{}")
        im.video = 1 if im.source_type_id == 2 or im.source_type_id == 3 else 0
        im.thumb = f'/thumbs/{im.image_id}.jpg'
        im.url_image = (f'/video/' if im.video else f'/image/') + str(im.image_id)
        return im

class ImageFavDto(AttrModel):
    id:int = Field(alias='image_id')
    fav:int

class ColorWithCoordsDto(BaseModel):
    hex:str
    x:float
    y:float

class ColorIdDto(AttrModel):
    id:int

class ColorDto(AttrModel):
    id:int
    x:float
    y:float
    hex:str

class ColorPaletteDto(BaseModel):
    id:int = Field(alias='image_id')
    palette:list[ColorDto]

class NextImageDto(BaseModel):
    id:int
    pattern:str