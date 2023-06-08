from models.models_lump import Session, ImageMetadata
import os

class ImageMetadataOverview:
    @staticmethod
    def get_overview():
        s = Session()
        images = s.query(ImageMetadata).group_by(ImageMetadata.path_id).order_by(ImageMetadata.study_type_id).all()
        return [OverviewPath.from_image_metadata(img) for img in images]


class OverviewPath:
    def __init__(self, path: str, path_id: int, study_type: str, count=0, image_id=-1):
        self.count = count
        self.path  = os.path.dirname(path)[len(study_type)+1:]
        self.path_id = path_id
        self.study_type = study_type
        self.image_id = image_id

    def __str__(self):
        return f'[path:{self.path} count:{self.count} id:{self.image_id}]'

    @staticmethod
    def from_image_metadata(img: 'ImageMetadata'):
        return OverviewPath(path=img.path, path_id=img.path_id, study_type=img.study_type, image_id=img.image_id)


if __name__ == "__main__":
    import os
    import sqlite3
    from Env import Env
    db = sqlite3.connect(Env.DB_FILE)
    res = ImageMetadataOverview.get_overview(db)

    for o in res:
        print(o)

