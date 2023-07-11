from models.models_lump import Session, ImageMetadata, Path

class ImageMetadataOverview:
    @staticmethod
    def get_overview(show_hidden:bool=False) -> [ImageMetadata]:
        s = Session()

        q = s.query(Path)
        if not show_hidden:
            q = q.filter(Path.hidden == 0)
        paths = q.order_by(Path.ord).all()

        images = []
        for p in paths:
            if p.preview == 0:
                im = s.query(ImageMetadata).filter(ImageMetadata.path_id == p.id).group_by(ImageMetadata.path_id).first()
            else:
                im = s.get(ImageMetadata, p.preview)
            im.path_ord = p.ord
            im.hidden = p.hidden
            im.path_dir = os.path.dirname(im.path)
            images.append(im)

        images = sorted(images, key=lambda i: (i.study_type_id, -i.path_ord))
        # images = s.query(ImageMetadata).group_by(ImageMetadata.path_id).order_by(ImageMetadata.study_type_id).all()
        return images


if __name__ == "__main__":
    import os
    import sqlite3
    from Env import Env
    db = sqlite3.connect(Env.DB_FILE)
    res = ImageMetadataOverview.get_overview(db)

    for o in res:
        print(o)

