from typing import Optional


class ViewFilterMultipleDTO:
    page: Optional[int] = 1
    offset: Optional[int] = None
    limit: Optional[int]  = None
    min_rating: Optional[int] = 0
    max_rating: Optional[int] = 9999

    image_ids: Optional[list] = None

    path_id: Optional[int] = None

    same_folder: Optional[int] = 0
    lost: Optional[int] = 0
    removed: Optional[int] = 0
    
    tag_set_name: Optional[str] = 'all'
    tag_set: Optional[int] = 1

    # tags_pos_raw: Optional[list] = None
    # tags_neg_raw: Optional[list] = None

    tags_pos: Optional[list] = None
    tags_neg: Optional[list] = None
    tags_pos_names: Optional[list] = None
    tags_neg_names: Optional[list] = None

    no_ai_tags: Optional[int] = None