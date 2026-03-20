from pydantic import BaseModel
from quart.json.provider import DefaultJSONProvider

from app.common.exceptions import AppError


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, AppError):
            return obj.to_dict()
        return super().default(obj)