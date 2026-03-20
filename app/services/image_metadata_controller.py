import os
from datetime import datetime

from quart import Request
from sqlalchemy import func

from app.common.folder_dtos import FilterRequestDto
from shared_utils.env import Env
from app.common.exceptions import ImageNotFoundError
from app.models import Session
from app.models.models_lump import Category, ImageMetadata, Path, ImageTag, ImageTagAi
from app.services.tags import get_tags_by_names, get_tags_by_set, get_tag_names

from shared_utils.utils import Utils


class ImageMetadataController:

    # region CRUD

    @staticmethod
    def create(path: str, categories=None, import_at=None, session=None) -> ImageMetadata|None:

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
    def get_or_raise(session:Session, image_id:int) -> ImageMetadata:
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
    def get_favs(filter_dto:FilterRequestDto, session) -> [ImageMetadata]:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
        q = q.filter(ImageMetadata.fav == 1).order_by(ImageMetadata.imported_at.desc())
        rows = q.offset(filter_dto.offset).limit(filter_dto.limit).all()
        return rows

    @staticmethod
    def get_last(filter_dto:FilterRequestDto, session) -> [ImageMetadata]:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
        rows = q.order_by(ImageMetadata.last_viewed.desc()).offset(filter_dto.offset).limit(filter_dto.limit).all()
        return rows

    @staticmethod
    def get_by_path(path, session=None) -> ImageMetadata|None:
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
    def get_all_by_path_id(filter_dto: FilterRequestDto, path_id:int, session=None) -> [ImageMetadata]:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session=session)
        rows = q.order_by(-ImageMetadata.rating,ImageMetadata.imported_at.desc(), ImageMetadata.filename).all()

        if len(rows) == 0:
            p = session.get(Path, path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].category, rows[0], rows

    @staticmethod
    def get_all_by_path_id2(filter_dto: FilterRequestDto, session=None) -> [ImageMetadata]:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session=session)
        q = q.order_by(-ImageMetadata.rating,ImageMetadata.imported_at.desc(), ImageMetadata.filename)
        q = q.offset(filter_dto.offset).limit(filter_dto.limit)

        rows = q.all()

        if len(rows) == 0:
            p = session.get(Path, filter_dto.path_id)
            return "", f'No images at path ({p.id}) "{p.path}"', []

        return rows[0].category, rows[0], rows

    @staticmethod
    def get_all_by_tags_new4(filter_dto:FilterRequestDto, session) -> [ImageMetadata]:
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
        q = q.order_by(ImageMetadata.imported_at.desc())

        result = q.offset(filter_dto.offset).limit(filter_dto.limit).all()

        return "", result

    @staticmethod
    def get_random_by_request(image_id, request:Request, session=None) -> 'ImageMetadata':
        # same_folder = request.args.get('sf', default=0, type=int)
        # min_rating  = request.args.get('r', default=0, type=int)

        data = request.args.to_dict()
        data['same-folder'] = data['sf'] if 'sf' in data else 0
        data['minr'] = data['r'] if 'r' in data else 0
        filter_dto = FilterRequestDto.model_validate(data)

        # tags_str = urllib.parse.unquote(request.args.get('tags', default=""))
        # tags_pos, tags_neg = handle_tags(tags_str)

        # tag_set_id = request.args.get('tag-set', default='all')
        # tag_set_id = tag_set_id if tag_set_id != '' else 'all'
        # tags_pos, tags_neg = get_tags_by_set(tag_set_id, session, tags_pos, tags_neg)

        # q = ImageMetadataController.get_query_imagemetadata(
        #     same_folder=same_folder, tags=(tags_pos, tags_neg),
        #     image_id=image_id, min_rating=min_rating, session=session)
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
        q = q.filter(ImageMetadata.image_id != image_id).order_by(func.random())
        row = q.first()

        return row

    @staticmethod
    def get_next_name_by_request(image_id:int, step:int, request:Request, session=None) -> ImageMetadata:
        # same_folder = 1
        # min_rating  = request.args.get('r', default=0, type=int)

        data = request.args.to_dict()
        data['same-folder'] = '1'
        filter_dto = FilterRequestDto.model_validate(data)

        im = ImageMetadataController.get_or_raise(session, image_id)

        # tags_str = urllib.parse.unquote(request.args.get('tags', default=""))
        # tags_pos, tags_neg = handle_tags(tags_str)
        #
        # tags_pos = get_tags_by_names(tags_pos, session=session)
        # tags_neg = get_tags_by_names(tags_neg, session=session)

        # q = ImageMetadataController.get_query_imagemetadata(
        #     same_folder=same_folder, tags=(tags_pos, tags_neg),
        #     image_id=image_id, min_rating=min_rating, session=session)
        q = ImageMetadataController.get_query_images_new4(filter_dto, session)
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
            q = q.outerjoin(ImageTagAi, ImageMetadata.image_id == ImageTagAi.image_id)\
                 .filter(ImageTagAi.image_id == None)

        # remove tags_neg
        if len(tags_neg_ids) > 0:
            q = q.filter(~ImageMetadata.tags.any(ImageTag.tag_id.in_(tags_neg_ids)))

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