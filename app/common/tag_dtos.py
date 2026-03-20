import urllib

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from app.utils.tags_helpers import handle_tags


class TagsRequestDto(BaseModel):
    raw:str = Field(alias='tags')
    pos: list[str] = Field(default= [])
    neg: list[str] = Field(default= [])

    @model_validator(mode='after')
    def parse_tags(self) -> Self:
        self.pos, self.neg = handle_tags(urllib.parse.unquote(self.raw))
        return self