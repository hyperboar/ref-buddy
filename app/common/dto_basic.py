from pydantic import BaseModel, ConfigDict


class EmptyResponse(BaseModel):
    pass

class AttrModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)