
class AppError(Exception):
    def to_dict(self):
        return {}

class EntityNotFoundError(AppError):
    def __init__(self,  id:int|list[int]|str|list[str], type:str, msg:str = 'ENTITY_NOT_FOUND'):
        self.id = id
        self.type = type
        super().__init__(msg)

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


class PathNotFoundError(EntityNotFoundError):
    def __init__(self, id:int|list[int]):
        super().__init__(id, 'path')

class PathEmptyError(EntityNotFoundError):
    def __init__(self, id:int|list[int]):
        super().__init__(id, 'path', 'PATH_IS_EMPTY')

class AnimationDataNotFoundError(EntityNotFoundError):
    def __init__(self, id:int, part:str):
        self.part = part
        super().__init__(id, 'animation')

    def to_dict(self):
        d = super().to_dict()
        d['part'] = self.part
        return d


class FileEntityNotFoundError(AppError):
    def __init__(self, id, path, msg:str = 'FILE_NOT_FOUND'):
        self.id = id
        self.path = path
        super().__init__(msg)

    def to_dict(self):
        return {'id': self.id, 'msg': str(self), 'path': self.path}

class ImageFileNotFoundError(FileEntityNotFoundError):
    def __init__(self, id:int, path:str):
        super().__init__(id, path)
