from app.models.models_lump import Session, Tag, TagSet


def get_tags_by_set(set_id :int |str, add_pos :[str ] =None, add_neg :[str ] =None, session=None):
    if session is None:
        session = Session()

    try:
        set_id = int(set_id)
    except ValueError:
        set_id = session.query(TagSet).filter(TagSet.set_alias == set_id).first().id


    tag_set = session.query(TagSet).filter(TagSet.id == set_id).first()
    tags_pos, tags_neg = tag_set.get_tags()

    add_pos = get_tags_by_names(add_pos, session=session) if add_pos and len \
        (add_pos) > 0 else []
    add_neg = get_tags_by_names(add_neg, session=session) if add_neg and len \
        (add_neg) > 0 else []

    tags_pos = list(set(tags_pos) - set(add_neg)) + add_pos
    tags_neg = list(set(tags_neg) - set(add_pos)) + add_neg

    return tags_pos, tags_neg

def get_all_tags(sort_by_name=False, session=None):
    if session is None:
        session = Session()

    tags = session.query(Tag).all()
    if sort_by_name:
        tags.sort(key=(lambda t : t.tag))
    return tags

def get_tags_by_names(tags: [str], session=None) -> [int]:
    if session is None:
        session = Session()
    rows = session.query(Tag).filter(Tag.tag.in_(tags)).all()
    return [row.id for row in rows]

def get_tag_names(tags: [int], session=None):
    if session is None:
        session = Session()
    found = session.query(Tag).filter(Tag.id.in_(tags)).all()
    return [t.tag for t in found]

def handle_tags(tag_str:str) -> ([str], [str]):
    tags_all = tag_str.split(',')
    tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
    tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

    return tags_pos, tags_neg