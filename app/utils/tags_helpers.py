def handle_tags(tag_str:str) -> ([str], [str]):
    if tag_str == '':
        return [], []
    tags_all = tag_str.split(',')
    tags_pos = [tag for tag in tags_all if not tag.startswith('-')]
    tags_neg = [tag[1:] for tag in tags_all if tag.startswith('-')]

    return tags_pos, tags_neg