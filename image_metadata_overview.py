from image_metadata import ImageMetadata
import sqlite3


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
        return images

        # qPaths = f"""
        # SELECT drop_filename(path) AS set_path, COUNT(*) AS image_count
        # FROM image_metadata
        # GROUP BY set_path
        # ORDER BY set_path
        # """
        # c.execute(qPaths)
        # rows = c.fetchall()
        # paths = [OverviewPath(path=row[0], count=row[1], image_id=ImageMetadata.get_id_by_path(conn, row[0])) for row in rows]
        # images = [ImageMetadata.get_by_id(conn, p.image_id) for p in paths]
        #
        # return paths, images


class OverviewPath:
    def __init__(self, path, count=0, image_id=-1):
        self.count = count
        self.path  = path
        self.image_id = image_id

    def __str__(self):
        return f'[path:{self.path} count:{self.count} id:{self.image_id}]'


if __name__ == "__main__":
    import os
    import sqlite3
    from Env import Env
    db = sqlite3.connect(Env.DB_FILE)
    res = ImageMetadataOverview.get_overview(db)

    for o in res:
        print(o)

