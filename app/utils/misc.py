import json
from datetime import datetime


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