from pydantic import BaseModel, ConfigDict, model_validator, ValidationError


class EmptyResponse(BaseModel):
    pass

class IntResultResponse(BaseModel):
    result:int

    @model_validator(mode='before')
    @classmethod
    def handle(cls, data):
        if not isinstance(data, int):
            raise ValidationError('Value is not int')
        return {'result': data}

class AttrModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)