import os
from datetime import datetime

from flask import Request

from Env import Env
from models.models_lump import Session, Tag, StudyType, ImageMetadata, Path, ImageTag, TagSet
from sqlalchemy import func

class ImageMetadataController:
    @staticmethod
    def get_table_schema() -> str:
        pass

    # region CRUD

    @staticmethod
    def create(path: str, study_types=None, import_at=None, session=None) -> 'ImageMetadata':

        dir = os.path.dirname(path)
        file = os.path.basename(path)

        stype_list = [s for s in study_types if dir.startswith(s.type)]

        if stype_list is None or len(stype_list) == 0:
            print(
                f"Path '{path}' should be in study_type named folder (These: {','.join([s.type for s in study_types])})")
            return None

        stype = stype_list[0]
        new_path = dir


        auto_commit = False
        if session is None:
            auto_commit = True
            session = Session()

        path_row = session.query(Path).filter(Path.path_raw == new_path).first()
        if path_row is None:
            path_ref = Path(path_raw=new_path)
            session.add(path_ref)
            session.commit()
            path_id = path_ref.id
        else:
            path_id = path_row.id

        source_type = ImageMetadata.source_type_by_path(os.path.join(Env.IMAGES_PATH, path))

        # print(f"inserting {(path_id, stype.id, file)} for path '{new_path}'")
        if import_at is None:
            new_image = ImageMetadata(path_id=path_id, study_type_id=stype.id, filename=file, source_type_id=source_type)
        else:
            new_image = ImageMetadata(path_id=path_id, study_type_id=stype.id, filename=file, source_type_id=source_type, imported_at=import_at)
        session.add(new_image)

        if auto_commit:
            session.commit()
        else:
            session.flush()

        return new_image

    # endregion CRUD

    # region Convenience

    @staticmethod
    def get_favs(count: int = 10000, start: int = 0, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None):
        if session is None:
            session = Session()

        q = ImageMetadataController.get_query_imagemetadata(tags=tags, min_rating=min_rating, session=session)
        q = q.filter(ImageMetadata.fav == 1).order_by(ImageMetadata.imported_at.desc())
        rows = q.offset(start).limit(count).all()
        return rows

    @staticmethod
    def get_last(count: int = 60, start: int = 0, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None):
        if session is None:
            session = Session()

        q = ImageMetadataController.get_query_imagemetadata(tags=tags, min_rating=min_rating, session=session)
        rows = q.order_by(ImageMetadata.last_viewed.desc()).offset(start).limit(count).all()
        return rows

    @staticmethod
    def get_by_id(image_id: int, session=None):
        if session is None:
            session = Session()
        return session.get(ImageMetadata, image_id)

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
    def get_all_by_path_id(path_id:int, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None) -> '[ImageMetadata]':
        if session is None:
            session = Session()

        q = ImageMetadataController.get_query_imagemetadata(path_id=path_id, tags=tags, min_rating=min_rating, session=session)
        rows = q.order_by(-ImageMetadata.rating,ImageMetadata.imported_at.desc(), ImageMetadata.filename).all()

        if len(rows) == 0:
            p = session.get(Path, path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].study_type, rows[0], rows

    @staticmethod
    def get_all_by_tags(tags_pos: [int], tags_neg: [int], limit:int=100, offset:int=0, session=None) -> '[ImageMetadata]':
        if session is None:
            session = Session()

        q = ImageMetadataController.get_query_imagemetadata(tags=(tags_pos, tags_neg), session=session)
        q = q.order_by(ImageMetadata.imported_at.desc())

        result = q.offset(offset).limit(limit).all()

        return "", result

    @staticmethod
    def get_tags_by_names(tags: [str], session=None) -> [int]:
        if session is None:
            session = Session()
        rows = session.query(Tag).filter(Tag.tag.in_(tags)).all()
        return [row.id for row in rows]

    @staticmethod
    def get_tags_by_set(set_id:int|str, add_pos:[str]=None, add_neg:[str]=None, session=None):
        if session is None:
            session = Session()

        try:
            set_id = int(set_id)
        except ValueError:
            set_id = session.query(TagSet).filter(TagSet.set_alias == set_id).first().id


        tag_set = session.query(TagSet).filter(TagSet.id == set_id).first()
        tags_pos, tags_neg = tag_set.get_tags()

        add_pos = ImageMetadataController.get_tags_by_names(add_pos, session=session) if add_pos and len(add_pos) > 0 else []
        add_neg = ImageMetadataController.get_tags_by_names(add_neg, session=session) if add_neg and len(add_neg) > 0 else []

        tags_pos = list(set(tags_pos) - set(add_neg)) + add_pos
        tags_neg = list(set(tags_neg) - set(add_pos)) + add_neg

        return tags_pos, tags_neg

    @staticmethod
    def get_random_by_study_type(study_type:int=0, same_folder:int=0, prev_image_id:int=0,
                                 min_rating=0, tags:([int],[int])=([],[]), session=None) -> 'ImageMetadata':
        if session is None:
            session = Session()

        q = ImageMetadataController.get_query_imagemetadata(
            study_type=study_type, same_folder=same_folder, tags=tags,
            image_id=prev_image_id, min_rating=min_rating, session=session)
        q = q.order_by(func.random())
        row = q.first()

        return row

    @staticmethod
    def get_random_by_request(image_id, request:Request, session=None) -> 'ImageMetadata':
        if session is None:
            raise Exception('No session')

        same_folder = request.args.get('sf', default=0, type=int)
        min_rating  = request.args.get('r', default=0, type=int)

        tags_str = request.args.get('tags', default="")
        tags_pos, tags_neg = ([], []) if tags_str == "" else ImageMetadataController.handle_tags(tags_str)

        tag_set_id = request.args.get('tag-set', default='all')
        tags_pos, tags_neg = ImageMetadataController.get_tags_by_set(tag_set_id, tags_pos, tags_neg, session=session)

        q = ImageMetadataController.get_query_imagemetadata(
            same_folder=same_folder, tags=(tags_pos, tags_neg),
            image_id=image_id, min_rating=min_rating, session=session)
        q = q.order_by(func.random())
        row = q.first()

        return row

    @staticmethod
    def handle_tags(tag_str:str) -> ([str], [str]):
        tags_all = tag_str.split(',')
        tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
        tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

        return tags_pos, tags_neg

    @staticmethod
    def get_next_name_by_request(image_id:int, step:int, request:Request, session=None) -> 'ImageMetadata':
        if session is None:
            raise Exception('No session')

        same_folder = 1
        min_rating  = request.args.get('r', default=0, type=int)

        im = session.get(ImageMetadata, image_id)

        tags_str = request.args.get('tags', default="")
        tags_pos, tags_neg = ([], []) if tags_str == "" else ImageMetadataController.handle_tags(tags_str)

        tags_pos = ImageMetadataController.get_tags_by_names(tags_pos, session=session)
        tags_neg = ImageMetadataController.get_tags_by_names(tags_neg, session=session)

        q = ImageMetadataController.get_query_imagemetadata(
            same_folder=same_folder, tags=(tags_pos, tags_neg),
            image_id=image_id, min_rating=min_rating, session=session)
        if step > 0:
            q = q.filter(ImageMetadata.filename > im.filename)
            q = q.order_by(ImageMetadata.filename)
        else:
            q = q.filter(ImageMetadata.filename < im.filename)
            q = q.order_by(ImageMetadata.filename.desc())
        row = q.first()

        if row is None:
            return im

        return row

    @staticmethod
    def get_query_imagemetadata(study_type:int=-1, same_folder:int=0, image_id:int=-1,
                                min_rating:int=0, tags:([int],[int])=([],[]),
                                path_id:int=-1, session=None):
        l = len(tags[0])

        # limit by tags_pos
        if l > 0:
            subquery = session.query(ImageTag.image_id)\
                .filter(ImageTag.tag_id.in_(tags[0]))\
                .group_by(ImageTag.image_id)\
                .having(func.count(ImageTag.tag_id) == l)\
                .subquery()
            q = session.query(ImageMetadata).join(subquery, ImageMetadata.image_id == subquery.c.image_id)
        else:
            q = session.query(ImageMetadata)

        # remove tags_neg
        if len(tags[1]) > 0:
            q = q.filter(~ImageMetadata.tags.any(ImageTag.tag_id.in_(tags[1])))

        # filter by study_type
        # if study_type > 0:
        #     q = q.filter(ImageMetadata.study_type_id == study_type, ImageMetadata.rating >= min_rating)

        # when same_folder get path_id by image_id
        if same_folder > 0 and image_id > 0:
            im = session.get(ImageMetadata, image_id)
            q = q.filter(ImageMetadata.path_id == im.path_id)

        # filter by path specifically
        if path_id > 0:
            q = q.filter(ImageMetadata.path_id == path_id)

        # unconditional min_rating
        q = q.filter(ImageMetadata.rating >= min_rating)
        q = q.filter(ImageMetadata.lost == 0)

        return q

    @staticmethod
    def set_image_fav(image_id: int, is_fav: int, session=None):
        if session is None:
            session = Session()

        im = session.get(ImageMetadata, image_id)
        im.fav = is_fav
        session.commit()
        return im

    @staticmethod
    def add_image_rating(image_id: int=None, rating_add: int=None, session=None) -> int:
        if session is None:
            session = Session()

        im = session.get(ImageMetadata, image_id)
        im.rating += rating_add
        session.commit()
        return im.rating

    @staticmethod
    def add_mult_image_rating(image_ids:[int]=None, rating_add: int=None, session=None) -> int:
        if session is None:
            session = Session()

        for im_id in image_ids:
            im = session.get(ImageMetadata, im_id)
            im.rating += rating_add
            session.flush()
        session.commit()
        return len(image_ids)

    @staticmethod
    def get_image_rating(image_id):
        s = Session()
        im = s.get(ImageMetadata, image_id)
        return im.rating

    @staticmethod
    def add_image_tags(image_ids: [int], tags_str: [str]) -> int:
        tags = ImageMetadataController.get_tags_by_names(tags_str)
        s = Session()
        for i in image_ids:
            [s.merge(ImageTag(image_id=i, tag_id=t)) for t in tags]
            s.flush()
        s.commit()
        return 1

    @staticmethod
    def remove_image_tags(image_ids: [int], tags_str: [str]) -> int:
        tags = ImageMetadataController.get_tags_by_names(tags_str)
        s = Session()
        q = s.query(ImageTag)\
            .filter(ImageTag.image_id.in_(image_ids))\
            .filter(ImageTag.tag_id.in_(tags))

        rows_to_delete = q.all()

        if len(rows_to_delete) == 0:
            return 0
        q.delete()
        s.commit()
        return len(rows_to_delete)


    @staticmethod
    def set_image_last_viewed(image_id: int, time: 'datetime'):
        s = Session()
        im = s.get(ImageMetadata, image_id)
        im.last_viewed = time
        im.count += 1
        s.commit()
        return im

    @staticmethod
    def get_id_by_path(path: str) -> int:
        img = ImageMetadataController.get_by_path(path)
        if img is None:
            return -1
        return img.image_id

    @staticmethod
    def get_study_types(session=None):
        if session is None:
            session = Session()
        return session.query(StudyType).all()

    @staticmethod
    def get_all_tags(sort_by_name=False, session=None):
        if session is None:
            session = Session()

        tags = session.query(Tag).all()
        if sort_by_name:
            tags.sort(key=(lambda t : t.tag))
        return tags

    @staticmethod
    def get_tag_names(tags: [int], session=None):
        if session is None:
            session = Session()
        found = session.query(Tag).filter(Tag.id.in_(tags)).all()
        return [t.tag for t in found]

    @staticmethod
    def update_paths_containing_images():
        """Goes through the IMAGES_PATH and adds missing entries to paths table."""
        session = Session()

        formats = tuple(Env.IMPORT_FORMATS)

        print('Updating folder paths registry...', end='')

        new_paths = []
        root_path = Env.IMAGES_PATH
        for dir_path, _, filenames in os.walk(root_path):

            if not any([f.endswith(formats) for f in filenames]):
                continue

            path = Path.path_serialize(os.path.relpath(dir_path, root_path))

            path_row = session.query(Path).filter(Path.path_raw == path).first()
            if path_row:
                continue

            path_ref = Path(path_raw=path)
            session.add(path_ref)
            session.flush()

            new_paths.append(path)

        session.rollback()
        # session.commit()

        print('\rUpdating folder paths registry... Done\n')

        if len(new_paths) > 0:
            print(f'Found {len(new_paths)} new folders')
            [print(f'{p}') for p in new_paths]

        pass

    # endregion Convenience


if __name__ == "__main__":
    print(ImageMetadataController.get_all_by_tags(None, [1, 24]))
    # print(ImageMetadataController.get_by_id(666))
    # print(ImageMetadataController.get_by_path('pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    # print(ImageMetadataController.get_id_by_path('pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    # print(ImageMetadataController.get_by_id(1666))
    # print(ImageMetadataController.get_by_id(2666))
    #
    # print('random')
    # print(ImageMetadataController.get_random_by_study_type(1))
    # print(ImageMetadataController.get_random_by_study_type(1))
    # print(ImageMetadataController.get_random_by_study_type(2, 1, 666))
    #
    # print('favs')
    # for img in ImageMetadataController.get_favs(count=2, start=3):
    #     print(img)
    #
    # print('last')
    # for img in ImageMetadataController.get_last(count=2, start=0):
    #     print(img)
    pass
