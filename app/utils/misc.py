import json
from datetime import datetime

from app.services.server_args_helpers import get_arg, Args


def json_for_folder_view(images, session=None) -> str:
    data = {'images': []}
    for im in images:
        print(im.imported_at)
        data['images'].append({
            'id': im.image_id,
            'r': im.rating,
            'fn': im.filename,
            'i_at': datetime.timestamp(im.imported_at)*1000,
            'video': 1 if im.source_type_id == 2 or im.source_type_id == 3 else 0
        })

    return json.dumps(data)


def get_offset_by_page(page:int, limit:int) -> int:
    return limit * page

def get_current_paging(args):
    """
    :param args: Web request args
    :return: page, offset, limit
    """
    limit = get_arg(args, Args.limit)
    page = get_arg(args, Args.page)
    offset = get_offset_by_page(page, limit)
    return page, offset, limit

def is_debugging():
    import sys
    return sys.gettrace() is not None