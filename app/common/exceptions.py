
class AppError(Exception):
    def to_dict(self):
        return {}

class EntityNotFoundError(AppError):
    def __init__(self,  id:int|list[int]|str|list[str], type:str):
        self.id = id
        self.type = type
        super().__init__('ENTITY_NOT_FOUND')

    def to_dict(self):
        return {'id': self.id, 'type': self.type, 'msg': str(self)}

class ImageNotFoundError(EntityNotFoundError):
    def __init__(self, id:int|list[int]):
        super().__init__(id, 'image')

class ThumbNotFoundError(EntityNotFoundError):
    def __init__(self, filename:str):
        super().__init__(filename, 'thumb')

class TagNotFoundError(EntityNotFoundError):
    def __init__(self, id:int|list[int]):
        super().__init__(id, 'tag')

class AnimationDataNotFoundError(EntityNotFoundError):
    def __init__(self, id:int, part:str):
        self.part = part
        super().__init__(id, 'animation')

    def to_dict(self):
        d = super().to_dict()
        d['part'] = self.part
        return d

class ImageFileNotFoundError(AppError):
    def __init__(self, id, path):
        self.id = id
        self.path = path
        super().__init__('FILE_NOT_FOUND')

    def to_dict(self):
        return {'id': self.id, 'msg': str(self), 'path': self.path}
