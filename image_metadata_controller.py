import os
from datetime import datetime

from models.models_lump import Session, Tag, StudyType, ImageMetadata, Path
from sqlalchemy import func

class ImageMetadataController:
    @staticmethod
    def get_table_schema() -> str:
        pass

    # region CRUD

    @staticmethod
    def create(path: str, study_types=None, session=None) -> 'ImageMetadata':

        dir = os.path.dirname(path)
        file = os.path.basename(path)

        stype_list = [s for s in study_types if dir.startswith(s.type)]

        if stype_list is None or len(stype_list) == 0:
            print(
                f"Path '{path}' should be in study_type named folder (These: {','.join([s.type for s in study_types])})")
            return None

        stype = stype_list[0]
        new_path = dir[len(stype.type) + 1:]

        if session is None:
            session = Session()

        path_row = session.query(Path).filter(Path.path == new_path).first()
        if path_row is None:
            path_ref = Path(path=new_path)
            session.add(path_ref)
            session.commit()
            path_id = path_ref.id
        else:
            path_id = path_row.id

        print(f"inserting {(path_id, stype.id, file)} for path '{new_path}'")
        new_image = ImageMetadata(path_id=path_id, study_type_id=stype.id, filename=file)
        session.add(new_image)
        session.commit()

        return new_image

    # endregion CRUD

    # region Convenience

    @staticmethod
    def get_favs(count: int = 10000, start: int = 0):
        s = Session()
        return s.query(ImageMetadata).filter(ImageMetadata.fav == 1).order_by(ImageMetadata.last_viewed.desc()).limit(count).offset(start).all()

    @staticmethod
    def get_last(count: int = 60, start: int = 0):
        s = Session()
        return s.query(ImageMetadata).order_by(ImageMetadata.last_viewed.desc()).limit(count).offset(start).all()

    @staticmethod
    def get_by_id(image_id: int):
        s = Session()
        return s.get(ImageMetadata, image_id)

    @staticmethod
    def get_by_path(path, session=None) -> 'ImageMetadata':
        if session is None:
            session = Session()

        filename = os.path.basename(path)
        rows = session.query(ImageMetadata).filter(ImageMetadata.filename == filename).all()
        if len(rows) == 0:
            return None

        targets = [row for row in rows if row.path == path]

        if len(targets) == 0:
            return None

        if len(targets) > 1:
            print(f"Found several images! ids:{'|'.join([f'{im.image_id}->{im.path_id}->{im.filename}' for im in rows])}")

        return targets[0]

    @staticmethod
    def get_all_by_path_id(path_id: int) -> '[ImageMetadata]':
        s = Session()

        rows = s.query(ImageMetadata).filter(ImageMetadata.path_id == path_id).all()
        if len(rows) == 0:
            p = s.get(Path, path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].study_type, rows[0], rows

    @staticmethod
    def get_all_by_tags(conn, tags: [int], limit=100, offset=0) -> '[ImageMetadata]':
        # c = conn.cursor()
        #
        # tag_str = ','.join([str(num) for num in tags])
        # # image ids
        # c.execute(f"""
        #         SELECT image_id, COUNT(DISTINCT tag_id) AS tag_count
        #         FROM image_tags
        #         WHERE tag_id IN ({tag_str})
        #         GROUP BY image_id
        #     """)
        # rows = c.fetchall()
        # if len(rows) == 0:
        #     return f"No images found for tags ({tag_str}) in tags", []
        #
        # image_ids = [str(row[0]) for row in rows if row[1] == len(tags)]
        #
        # c.execute(
        #     f"{ImageMetadata.BASE_Q} WHERE im.id IN ({','.join(image_ids)}) ORDER BY im.imported_at  LIMIT {limit} OFFSET {offset}")
        #
        # rows = c.fetchall()
        # if len(rows) == 0:
        #     return f"No images found for tags ({tag_str}) in images", []
        #
        # images = [ImageMetadata.from_full_row(row) for row in rows]
        #
        # return "", images
        pass

    @staticmethod
    def get_random_by_study_type(study_type: int, same_folder: int = 0, prev_image_id: int = -1,
                                 min_rating=0) -> 'ImageMetadata':
        s = Session()

        q = s.query(ImageMetadata).order_by(func.random())
        q = q.filter(ImageMetadata.study_type_id == study_type, ImageMetadata.rating >= min_rating)

        if same_folder > 0 and prev_image_id > 0:
            im = s.get(ImageMetadata, prev_image_id)
            q = q.filter(ImageMetadata.path_id == im.path_id)

        return q.first()

    @staticmethod
    def set_image_fav(image_id: int, is_fav: int):
        s = Session()
        im = s.get(ImageMetadata, image_id)
        im.fav = is_fav
        s.commit()
        return im

    @staticmethod
    def add_image_rating(image_id: int, rating_add: int) -> int:
        s = Session()
        im = s.get(ImageMetadata, image_id)
        im.rating += rating_add
        s.commit()
        return 1

    @staticmethod
    def set_image_last_viewed(image_id: int, time: 'datetime'):
        s = Session()
        im = s.get(ImageMetadata, image_id)
        im.last_viewed = time
        s.commit()
        return im

    @staticmethod
    def get_id_by_path(path: str) -> int:
        img = ImageMetadataController.get_by_path(path)
        if img is None:
            return -1
        return img.image_id

    @staticmethod
    def get_study_types():
        s = Session()
        return s.query(StudyType).all()

    @staticmethod
    def get_all_tags():
        s = Session()
        return s.query(Tag).all()

    @staticmethod
    def get_tag_names(tags: [int]):
        s = Session()
        found = s.query(Tag).filter(
            tags.contains(Tag.id.in_(tags)) # ??
        ).all()
        return [t.tag for t in found]

    # endregion Convenience


if __name__ == "__main__":
    print(ImageMetadataController.get_by_id(666))
    print(ImageMetadataController.get_by_path('pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    print(ImageMetadataController.get_id_by_path('pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    print(ImageMetadataController.get_by_id(1666))
    print(ImageMetadataController.get_by_id(2666))

    print('random')
    print(ImageMetadataController.get_random_by_study_type(1))
    print(ImageMetadataController.get_random_by_study_type(1))
    print(ImageMetadataController.get_random_by_study_type(2, 1, 666))

    print('favs')
    for img in ImageMetadataController.get_favs(count=2, start=3):
        print(img)

    print('last')
    for img in ImageMetadataController.get_last(count=2, start=0):
        print(img)
    pass
