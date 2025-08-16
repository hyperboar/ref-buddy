import urllib

from flask import Request

from Env import Env
from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Session
from models.view_filter_dto import ViewFilterMultipleDTO


class ViewFilterMapper:
    def request_to_filter_multiple_dto(self, request: Request) -> ViewFilterMultipleDTO:
        dto = ViewFilterMultipleDTO()

        dto.page = request.args.get(key='page', type=int) or dto.page
        dto.page = dto.page - 1

        dto.limit = request.args.get(key='limit', type=int) or Env.DEFAULT_PER_PAGE_LIMIT
        dto.offset = dto.limit * dto.page

        dto.min_rating = request.args.get(key='minr', type=int) or dto.min_rating
        dto.max_rating = request.args.get(key='maxr', type=int) or dto.max_rating
        
        #tags        
        dto.tag_set_name = request.args.get('tag-set') or dto.tag_set_name

        tags_all = urllib.parse.unquote(request.args.get('tags') or "", encoding='utf-8', errors='replace').split(',')
        tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
        tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

        session = Session()
        tags_pos, tags_neg = Ctrl.get_tags_by_set(dto.tag_set_name, tags_pos, tags_neg, session=session)
        tags_pos_names = Ctrl.get_tag_names(tags_pos, session=session)
        tags_neg_names = Ctrl.get_tag_names(tags_neg, session=session)
        dto.tags_pos = tags_pos
        dto.tags_neg = tags_neg
        dto.tags_pos_names = tags_pos_names
        dto.tags_neg_names = tags_neg_names

        return dto

    def request_to_filter_single_dto(self, request: Request) -> ViewFilterMultipleDTO:
        pass