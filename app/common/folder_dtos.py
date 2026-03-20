import json
from typing import Annotated

from pydantic import BaseModel, Field, model_validator, AfterValidator
from typing_extensions import Self

from app.common.dto_basic import AttrModel
from app.common.tag_dtos import TagsRequestDto
from shared_utils.env import Env


class FilterRequestDto(BaseModel):
    page:Annotated[int, AfterValidator(lambda v: max(v - 1, 0))] = Field(default=0)
    limit:int = Field(default=Env.DEFAULT_PER_PAGE_LIMIT)
    offset:int|None = None
    no_ai_tags:int = Field(default=1, alias='no-ai-tags')
    min_rating:int = Field(default=0, alias='minr')
    max_rating:int = Field(default=9999, alias='maxr')
    tag_set:int|str = Field(default='all', alias='tag-set')
    tags:TagsRequestDto
    image_ids:list[int]|None = Field(default=None, alias='image-ids')
    same_folder:int|None = Field(default=None, alias='same-folder')
    path_id:int|None = Field(default=None, alias='path-id')

    @model_validator(mode='before')
    @classmethod
    def parse_tags(cls, values):
        values['tags'] = {'tags': (values['tags'] if 'tags' in values else '')}
        values['image-ids'] = values['image-ids'].split(',') if 'image-ids' in values else None
        return values

    @model_validator(mode='after')
    def post(self) -> Self:
        self.offset = self.page * self.limit
        return self

class FolderExportDto(AttrModel):
    id:int = Field(alias='image_id')
    url:str = None

    @model_validator(mode='after')
    def validate_url(self) -> Self:
        self.url = f"/image/{ self.id }"
        return self