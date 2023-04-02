from image_metadata import ImageMetadata
import sqlite3
import os


# def drop_filename(path):
#     import os
#     return os.path.dirname(path)


class ImageMetadataOverview:
    @staticmethod
    def get_overview(conn):
        c = conn.cursor()

        # conn.create_function("drop_filename", 1, drop_filename)

        c.execute(f"select id, path, study_type from {ImageMetadata.TABLE_NAME} group by path order by study_type ")

        rows = c.fetchall()
        images = [ImageMetadata.get_by_id(conn, row[0]) for row in rows]
        return [OverviewPath.from_image_metadata(img) for img in images]


class OverviewPath:
    def __init__(self, path: str, study_type: str, count=0, image_id=-1):
        self.count = count
        self.path  = os.path.dirname(path)[len(study_type)+1:]
        self.study_type = study_type
        self.image_id = image_id

    def __str__(self):
        return f'[path:{self.path} count:{self.count} id:{self.image_id}]'

    @staticmethod
    def from_image_metadata(img: 'ImageMetadata'):
        return OverviewPath(path=img.path, study_type=img.study_type, image_id=img.image_id)


if __name__ == "__main__":
    import os
    import sqlite3
    from Env import Env
    db = sqlite3.connect(Env.DB_FILE)
    res = ImageMetadataOverview.get_overview(db)

    for o in res:
        print(o)

