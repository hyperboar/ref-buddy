import os
import urllib
from datetime import datetime

from quart import Request
from typing_extensions import deprecated
from sqlalchemy import func

from app.common.folder_dtos import FilterRequestDto
from shared_utils.env import Env
from app.utils.tags_helpers import handle_tags
from app.common.exceptions import ImageNotFoundError
from app.models import Session
from app.models.models_lump import Category, ImageMetadata, Path, ImageTag, ImageTagAi
from app.services.tags import get_tags_by_names, get_tags_by_set, get_tag_names

from shared_utils.utils import Utils


class ImageMetadataController:
    @staticmethod
    def get_table_schema() -> str:
        pass

    # region CRUD

    @staticmethod
    def create(path: str, categories=None, import_at=None, session=None) -> 'ImageMetadata':

        dir = os.path.dirname(path)
        file = os.path.basename(path)

        cat_list = [s for s in categories if dir.startswith(s.category)]

        if cat_list is None or len(cat_list) == 0:
            print(
                f"Path '{path}' should be in study_type named folder (These: {','.join([s.category for s in categories])})")
            return None

        ctg = cat_list[0]
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

        # print(f"inserting {(path_id, ctg.id, file)} for path '{new_path}'")
        if import_at is None:
            new_image = ImageMetadata(path_id=path_id, category_id=ctg.id, filename=file, source_type_id=source_type)
        else:
            new_image = ImageMetadata(path_id=path_id, category_id=ctg.id, filename=file, source_type_id=source_type, imported_at=import_at)
        session.add(new_image)

        if auto_commit:
            session.commit()
        else:
            session.flush()

        return new_image

    # endregion CRUD

    # region Convenience

    @staticmethod
    def get_or_raise(session:Session, image_id:int) -> ImageMetadata | None:
        img = session.get(ImageMetadata, image_id)
        if img is None:
            raise ImageNotFoundError(image_id)
        return img

    @staticmethod
    def all_exist_or_raise(session:Session, image_ids:[int]) -> bool:
        count = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(image_ids)).count()
        if count < len(image_ids):
            raise ImageNotFoundError(image_ids)
        return True

    @staticmethod
    def get_favs(count: int = 10000, start: int = 0, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None):
        q = ImageMetadataController.get_query_imagemetadata(tags=tags, min_rating=min_rating, session=session)
        q = q.filter(ImageMetadata.fav == 1).order_by(ImageMetadata.imported_at.desc())
        rows = q.offset(start).limit(count).all()
        return rows

    @staticmethod
    def get_last(count: int = 60, start: int = 0, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None):
        q = ImageMetadataController.get_query_imagemetadata(tags=tags, min_rating=min_rating, session=session)
        rows = q.order_by(ImageMetadata.last_viewed.desc()).offset(start).limit(count).all()
        return rows

    @staticmethod
    def get_by_path(path, session=None) -> 'ImageMetadata':
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
        q = ImageMetadataController.get_query_imagemetadata(path_id=path_id, tags=tags, min_rating=min_rating, session=session)
        rows = q.order_by(-ImageMetadata.rating,ImageMetadata.imported_at.desc(), ImageMetadata.filename).all()

        if len(rows) == 0:
            p = session.get(Path, path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].category, rows[0], rows

    @staticmethod
    # def get_all_by_path_id2(path_id:int, tags:([int],[int])=([],[]), min_rating:int=-1000, session=None) -> '[ImageMetadata]':
    # def get_all_by_path_id2(params: ViewFilterMultipleDTO, session=None) -> '[ImageMetadata]':
    def get_all_by_path_id2(params: FilterRequestDto, session=None) -> '[ImageMetadata]':
        # q = ImageMetadataController.get_query_imagemetadata_new3(path_id=path_id, tags=tags, min_rating=min_rating, session=session)
        q = ImageMetadataController.get_query_images_new4(params, session=session)
        q = q.order_by(-ImageMetadata.rating,ImageMetadata.imported_at.desc(), ImageMetadata.filename)
        q = q.offset(params.offset).limit(params.limit)

        rows = q.all()

        if len(rows) == 0:
            p = session.get(Path, params.path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].category, rows[0], rows

    @deprecated('not in use')
    @staticmethod
    def get_all_by_tags(tags_pos: [int], tags_neg: [int], limit:int=100, offset:int=0, session=None) -> '[ImageMetadata]':
        q = ImageMetadataController.get_query_imagemetadata(tags=(tags_pos, tags_neg), session=session)
        q = q.order_by(ImageMetadata.imported_at.desc())

        result = q.offset(offset).limit(limit).all()

        return "", result

    # @staticmethod
    # # def get_all_by_tags_new2(tags_pos: [int], tags_neg: [int], limit:int=100, offset:int=0, session=None) -> '[ImageMetadata]':
    # def get_all_by_tags_new2(params, session=None) -> '[ImageMetadata]':
    #     q = ImageMetadataController.get_query_imagemetadata_new2(params, session=session)
    #     q = q.order_by(ImageMetadata.imported_at.desc())
    #
    #     result = q.offset(params['offset']).limit(params['limit']).all()
    #
    #     return "", result

    # @staticmethod
    # # def get_all_by_tags_new2(tags_pos: [int], tags_neg: [int], limit:int=100, offset:int=0, session=None) -> '[ImageMetadata]':
    # def get_all_by_tags_new3(params: ViewFilterMultipleDTO, session=None) -> '[ImageMetadata]':
    #     q = ImageMetadataController.get_query_imagemetadata_new3(params, session=session)
    #     q = q.order_by(ImageMetadata.imported_at.desc())
    #
    #     result = q.offset(params.offset).limit(params.limit).all()
    #
    #     return "", result

    @staticmethod
    # def get_all_by_tags_new2(tags_pos: [int], tags_neg: [int], limit:int=100, offset:int=0, session=None) -> '[ImageMetadata]':
    # def get_all_by_tags_new3(params:FilterRequestDto, session) -> '[ImageMetadata]':
    def get_all_by_tags_new4(params:FilterRequestDto, session) -> '[ImageMetadata]':
        q = ImageMetadataController.get_query_images_new4(params, session)
        q = q.order_by(ImageMetadata.imported_at.desc())

        result = q.offset(params.offset).limit(params.limit).all()

        return "", result



    @staticmethod
    def get_random_by_category(category:int=0, same_folder:int=0, prev_image_id:int=0,
                               min_rating=0, tags:([int],[int])=([],[]), session=None) -> 'ImageMetadata':
        q = ImageMetadataController.get_query_imagemetadata(
            category=category, same_folder=same_folder, tags=tags,
            image_id=prev_image_id, min_rating=min_rating, session=session)
        q = q.order_by(func.random())
        row = q.first()

        return row

    @staticmethod
    def get_random_by_request(image_id, request:Request, session=None) -> 'ImageMetadata':
        same_folder = request.args.get('sf', default=0, type=int)
        min_rating  = request.args.get('r', default=0, type=int)

        tags_str = urllib.parse.unquote(request.args.get('tags', default=""))
        tags_pos, tags_neg = handle_tags(tags_str)

        tag_set_id = request.args.get('tag-set', default='all')
        tag_set_id = tag_set_id if tag_set_id != '' else 'all'
        tags_pos, tags_neg = get_tags_by_set(tag_set_id, session, tags_pos, tags_neg)

        q = ImageMetadataController.get_query_imagemetadata(
            same_folder=same_folder, tags=(tags_pos, tags_neg),
            image_id=image_id, min_rating=min_rating, session=session)
        q = q.filter(ImageMetadata.image_id != image_id).order_by(func.random())
        row = q.first()

        return row

    @staticmethod
    def get_next_name_by_request(image_id:int, step:int, request:Request, session=None) -> 'ImageMetadata':
        same_folder = 1
        min_rating  = request.args.get('r', default=0, type=int)

        im = session.get(ImageMetadata, image_id)

        tags_str = urllib.parse.unquote(request.args.get('tags', default=""))
        tags_pos, tags_neg = handle_tags(tags_str)

        tags_pos = get_tags_by_names(tags_pos, session=session)
        tags_neg = get_tags_by_names(tags_neg, session=session)

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
    def get_query_imagemetadata(category:int=-1, same_folder:int=0, image_id:int=-1,
                                min_rating:int=0, max_rating=9999, tags:([int],[int])=([],[]),
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

        # filter by category
        # if category > 0:
        #     q = q.filter(ImageMetadata.category_id == category, ImageMetadata.rating >= min_rating)

        # when same_folder get path_id by image_id
        if same_folder > 0 and image_id > 0:
            im = session.get(ImageMetadata, image_id)
            q = q.filter(ImageMetadata.path_id == im.path_id)

        # filter by path specifically
        if path_id > 0:
            q = q.filter(ImageMetadata.path_id == path_id)

        # unconditional min_rating
        q = q.filter(min_rating <= ImageMetadata.rating, ImageMetadata.rating <= max_rating)
        q = q.filter(ImageMetadata.lost == 0)
        q = q.filter(ImageMetadata.removed == 0)

        return q

    # @staticmethod
    # def get_query_imagemetadata_new2(params, session=None):
    #     l = len(params['tags_pos'])
    #
    #     # limit by tags_pos
    #     if l > 0:
    #         subquery = session.query(ImageTag.image_id)\
    #             .filter(ImageTag.tag_id.in_(params['tags_pos']))\
    #             .group_by(ImageTag.image_id)\
    #             .having(func.count(ImageTag.tag_id) == l)\
    #             .subquery()
    #         q = session.query(ImageMetadata).join(subquery, ImageMetadata.image_id == subquery.c.image_id)
    #     else:
    #         q = session.query(ImageMetadata)
    #
    #     if 'no_ai_tags' in params and params['no_ai_tags'] == 1:
    #         # subquery = session.query(ImageTagAi.image_id)\
    #         #     .group_by(ImageTagAi.image_id)\
    #         #     .subquery()
    #         # q = q.join(subquery, ImageMetadata.image_id != subquery.c.image_id)
    #         q = q.outerjoin(ImageTagAi, ImageMetadata.image_id == ImageTagAi.image_id)\
    #              .filter(ImageTagAi.image_id == None)
    #
    #     # remove tags_neg
    #     if len(params['tags_neg']) > 0:
    #         q = q.filter(~ImageMetadata.tags.any(ImageTag.tag_id.in_(params['tags_neg'])))
    #
    #     # filter by category
    #     # if category > 0:
    #     #     q = q.filter(ImageMetadata.category_id == category, ImageMetadata.rating >= min_rating)
    #
    #     # when same_folder get path_id by image_id
    #     if params['same_folder'] > 0 and len(params['image_ids']) > 0:
    #         im = session.get(ImageMetadata, params['image_ids'][0])
    #         q = q.filter(ImageMetadata.path_id == im.path_id)
    #
    #     # filter by path specifically
    #     if params['path_id'] is not None:
    #         q = q.filter(ImageMetadata.path_id == params['path_id'])
    #
    #     # unconditional min_rating
    #     q = q.filter(params['min_rating'] <= ImageMetadata.rating, ImageMetadata.rating <= params['max_rating'])
    #     q = q.filter(ImageMetadata.lost == 0)
    #     q = q.filter(ImageMetadata.removed == 0)
    #
    #     return q

    # @staticmethod
    # def get_query_imagemetadata_new3(params:ViewFilterMultipleDTO, session=None):
    #     l = len(params.tags_pos)
    #
    #     # limit by tags_pos
    #     if l > 0:
    #         subquery = session.query(ImageTag.image_id)\
    #             .filter(ImageTag.tag_id.in_(params.tags_pos))\
    #             .group_by(ImageTag.image_id)\
    #             .having(func.count(ImageTag.tag_id) == l)\
    #             .subquery()
    #         q = session.query(ImageMetadata).join(subquery, ImageMetadata.image_id == subquery.c.image_id)
    #     else:
    #         q = session.query(ImageMetadata)
    #
    #     if params.no_ai_tags is not None and params.no_ai_tags == 1:
    #         # subquery = session.query(ImageTagAi.image_id)\
    #         #     .group_by(ImageTagAi.image_id)\
    #         #     .subquery()
    #         # q = q.join(subquery, ImageMetadata.image_id != subquery.c.image_id)
    #         q = q.outerjoin(ImageTagAi, ImageMetadata.image_id == ImageTagAi.image_id)\
    #              .filter(ImageTagAi.image_id == None)
    #
    #     # remove tags_neg
    #     if len(params.tags_neg) > 0:
    #         q = q.filter(~ImageMetadata.tags.any(ImageTag.tag_id.in_(params.tags_neg)))
    #
    #     # filter by category
    #     # if category > 0:
    #     #     q = q.filter(ImageMetadata.category_id == category, ImageMetadata.rating >= min_rating)
    #
    #     # when same_folder get path_id by image_id
    #     if params.same_folder > 0 and len(params.image_ids) > 0:
    #         im = session.get(ImageMetadata, params.image_ids[0])
    #         q = q.filter(ImageMetadata.path_id == im.path_id)
    #
    #     # filter by path specifically
    #     if params.path_id is not None:
    #         q = q.filter(ImageMetadata.path_id == params.path_id)
    #
    #     # unconditional min_rating
    #     q = q.filter(params.min_rating <= ImageMetadata.rating, ImageMetadata.rating <= params.max_rating)
    #     q = q.filter(ImageMetadata.lost == 0)
    #     q = q.filter(ImageMetadata.removed == 0)
    #
    #     return q

    @staticmethod
    def get_query_images_new4(filter_dto:FilterRequestDto, session):

        tags_pos_ids, tags_neg_ids = get_tags_by_set(filter_dto.tag_set, session, filter_dto.tags.pos, filter_dto.tags.neg)

        if Utils.is_debugging():
            tags_pos_names = get_tag_names(tags_pos_ids, session)
            tags_neg_names = get_tag_names(tags_neg_ids, session)

        l = len(tags_pos_ids)

        # limit by tags_pos
        if l > 0:
            subquery = session.query(ImageTag.image_id)\
                .filter(ImageTag.tag_id.in_(tags_pos_ids))\
                .group_by(ImageTag.image_id)\
                .having(func.count(ImageTag.tag_id) == l)\
                .subquery()
            q = session.query(ImageMetadata).join(subquery, ImageMetadata.image_id == subquery.c.image_id)
        else:
            q = session.query(ImageMetadata)

        if filter_dto.no_ai_tags is not None and filter_dto.no_ai_tags == 1:
            # subquery = session.query(ImageTagAi.image_id)\
            #     .group_by(ImageTagAi.image_id)\
            #     .subquery()
            # q = q.join(subquery, ImageMetadata.image_id != subquery.c.image_id)
            q = q.outerjoin(ImageTagAi, ImageMetadata.image_id == ImageTagAi.image_id)\
                 .filter(ImageTagAi.image_id == None)

        # remove tags_neg
        if len(tags_neg_ids) > 0:
            q = q.filter(~ImageMetadata.tags.any(ImageTag.tag_id.in_(tags_neg_ids)))

        # filter by category
        # if category > 0:
        #     q = q.filter(ImageMetadata.category_id == category, ImageMetadata.rating >= min_rating)

        # when same_folder get path_id by image_id
        if filter_dto.same_folder is not None and len(filter_dto.image_ids) > 0:
            im = session.get(ImageMetadata, filter_dto.image_ids[0])
            q = q.filter(ImageMetadata.path_id == im.path_id)

        # filter by path specifically
        if filter_dto.path_id is not None:
            q = q.filter(ImageMetadata.path_id == filter_dto.path_id)

        # unconditional min_rating
        q = q.filter(filter_dto.min_rating <= ImageMetadata.rating, ImageMetadata.rating <= filter_dto.max_rating)
        q = q.filter(ImageMetadata.lost == 0)
        q = q.filter(ImageMetadata.removed == 0)

        return q

    @classmethod
    def set_image_fav(cls, image_id: int, is_fav: int, session=None):
        im = cls.get_or_raise(session, image_id)
        im.fav = is_fav
        session.commit()
        return im

    @classmethod
    def add_image_rating(cls, image_id: int=None, rating_add: int=None, session=None) -> int:
        im = cls.get_or_raise(session, image_id)
        im.rating += rating_add
        session.commit()
        return im.rating

    @staticmethod
    def add_mult_image_rating(image_ids:[int]=None, rating_add: int=None, session=None) -> int:
        for im_id in image_ids:
            im = session.get(ImageMetadata, im_id)
            im.rating += rating_add
            session.flush()
        session.commit()
        return len(image_ids)

    @staticmethod
    def add_image_tags(image_ids: [int], tags_str: [str], session=None) -> int:
        tags = get_tags_by_names(tags_str, session)

        for i in image_ids:
            [session.merge(ImageTag(image_id=i, tag_id=t)) for t in tags]
            session.flush()
        session.commit()
        return len(image_ids) * len(tags)

    @staticmethod
    def remove_image_tags(image_ids: [int], tags_str: [str], session=None) -> int:
        tags = get_tags_by_names(tags_str, session)
        q = session.query(ImageTag)\
            .filter(ImageTag.image_id.in_(image_ids))\
            .filter(ImageTag.tag_id.in_(tags))

        rows_to_delete = q.all()

        if len(rows_to_delete) == 0:
            return 0
        q.delete()
        session.commit()
        return len(rows_to_delete)


    @classmethod
    def set_image_last_viewed(cls, session, image_id: int, time: 'datetime'):
        im = cls.get_or_raise(session, image_id)
        im.last_viewed = time
        im.count += 1
        session.commit()
        return im

    @deprecated('not in use')
    @staticmethod
    def get_id_by_path(path: str) -> int:
        img = ImageMetadataController.get_by_path(path)
        if img is None:
            return -1
        return img.image_id

    @staticmethod
    def get_categories(session=None):
        return session.query(Category).all()


    @staticmethod
    def update_paths_containing_images(session=None, auto_commit=True):
        """Goes through the IMAGES_PATH and adds missing entries to paths table."""
        if session is None:
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

        session.flush()

        if auto_commit:
            session.commit()

        print('\rUpdating folder paths registry... Done\n')

        if len(new_paths) > 0:
            print(f'Found {len(new_paths)} new folders')
            [print(f'{p}') for p in new_paths]

        pass

    # endregion Convenience


if __name__ == "__main__":
    # print(ImageMetadataController.get_all_by_tags(None, [1, 24]))
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
