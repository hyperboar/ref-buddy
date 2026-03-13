from typing_extensions import deprecated

from app.models import Session
from app.models.models_lump import Tag, TagSet


def get_tags_by_set(set_id:int|str, session:Session, add_pos:[str]=None, add_neg:[str]=None):

    try:
        set_id = int(set_id)
    except ValueError:
        set_id = session.query(TagSet).filter(TagSet.set_alias == set_id).first().id


    tag_set = session.query(TagSet).filter(TagSet.id == set_id).first()
    tags_pos, tags_neg = tag_set.get_tags()

    add_pos = get_tags_by_names(add_pos, session=session) if add_pos and len(add_pos) > 0 else []
    add_neg = get_tags_by_names(add_neg, session=session) if add_neg and len(add_neg) > 0 else []

    tags_pos = list((set(tags_pos) - set(add_neg)).union(set(add_pos)))
    tags_neg = list((set(tags_neg) - set(add_pos)).union(set(add_neg)))

    return tags_pos, tags_neg

@deprecated('')
def get_all_tags(session:Session, sort_by_name=False):

    tags = session.query(Tag).all()
    if sort_by_name:
        tags.sort(key=(lambda t : t.tag))
    return tags

def get_tags_by_names(tags: [str], session:Session) -> [int]:
    if tags is None or len(tags) == 0: return []

    rows = session.query(Tag).filter(Tag.tag.in_(tags)).all()
    return [row.id for row in rows]

def get_tag_names(tags: [int], session:Session):
    if tags is None or len(tags) == 0: return []

    found = session.query(Tag).filter(Tag.id.in_(tags)).all()
    return [t.tag for t in found]

def handle_tags(tag_str:str) -> ([str], [str]):
    if tag_str == '':
        return [], []
    tags_all = tag_str.split(',')
    tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
    tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

    return tags_pos, tags_neg