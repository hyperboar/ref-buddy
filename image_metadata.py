import os
import sqlite3
import random
from string import Template

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

IMAGES_PATH = os.getenv('IMAGES_PATH')

def full_image_path(st, path, file):
    import os
    return os.path.join(st, path, file)

class ImageMetadata:
    TABLE_NAME = "image_metadata"
    FIELDS = None
    BASE_Q = f"SELECT im.*, st.type AS study_type, pr.path AS path_full FROM image_metadata AS im JOIN study_types AS st ON im.study_type = st.id JOIN paths AS pr ON im.path = pr.id"

    def __init__(self, path, filename=None, count=0, time_spent=0, facing=0, last_viewed=0, idx=-1, diff=0, study_type=None, is_fav=0,
                 path_id=0, study_type_id=0):
        self.image_id = idx
        self.path = os.path.join(study_type, path, filename)
        self.path_id = path_id
        self.study_type = study_type
        self.study_type_id = study_type_id
        self.last_viewed = last_viewed
        self.is_fav = is_fav

        self.count = count
        self.difficulty = diff
        self.facing = facing
        self.time_spent = time_spent

    @staticmethod
    def static_initialize(conn):
        ImageMetadata.get_fields(conn)

    @staticmethod
    def get_fields(conn=None):
        if ImageMetadata.FIELDS is not None:
            return ImageMetadata.FIELDS

        if conn is None:
            return None

        c = conn.cursor()
        c.execute(f"PRAGMA table_info({ImageMetadata.TABLE_NAME})")
        results = c.fetchall()
        list = [row for row in results]
        list.append((len(results), 'study_type_name'))
        list.append((len(results)+1, 'path_full'))
        ImageMetadata.FIELDS = {row[1]: row[0] for row in list}

        return ImageMetadata.FIELDS

    @staticmethod
    def get_table_schema() -> str:
        return f"""
            PRAGMA foreign_keys = ON;
            
            CREATE TABLE IF NOT EXISTS {ImageMetadata.TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                facing INTEGER DEFAULT 0,
                last_viewed TIMESTAMP DEFAULT 0,
                difficulty INTEGER DEFAULT 10,
                fav INTEGER DEFAULT 0,
                lost INTEGER DEFAULT 0,
                FOREIGN KEY (path) REFERENCES paths (id),
                FOREIGN KEY (study_type) REFERENCES study_type (id),
                FOREIGN KEY (facing) REFERENCES facings (id)
            )
            
            CREATE TABLE IF NOT EXISTS paths (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS study_types (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL UNIQUE
            );
            
            INSERT INTO study_type (type) VALUES ('academic');
            INSERT INTO study_type (type) VALUES ('pron');
            INSERT INTO study_type (type) VALUES ('artist');
            
            CREATE TABLE IF NOT EXISTS poses (
                id INTEGER PRIMARY KEY,
                pose TEXT NOT NULL UNIQUE
            );
            
            INSERT INTO poses (pose) VALUES ('stand');
            INSERT INTO poses (pose) VALUES ('sit');
            INSERT INTO poses (pose) VALUES ('lay');
            INSERT INTO poses (pose) VALUES ('stand_bent');
            
            CREATE TABLE facings (
                id INTEGER PRIMARY KEY,
                facing TEXT NOT NULL UNIQUE
            );
            
            INSERT INTO facings (facing) VALUES ('front');
            INSERT INTO facings (facing) VALUES ('back');
            INSERT INTO facings (facing) VALUES ('side');
            INSERT INTO facings (facing) VALUES ('3/4');
            INSERT INTO facings (facing) VALUES ('top');
            INSERT INTO facings (facing) VALUES ('bottom');
        """


    # def save(self, conn):
    #     c = conn.cursor()
    #     c.execute(
    #         f"INSERT INTO {ImageMetadata.TABLE_NAME} (path, usage_count, time_spent_watching, facing, last_viewed) "
    #         f"VALUES (?, ?, ?, ?, ?)",
    #         (self.path, self.usage_count, self.time_spent_watching, self.facing, self.last_viewed)
    #     )
    #     conn.commit()

    # def to_tuple(self):
    #     return (self.path, self.count, self.time_spent, self.facing)

    # region CRUD

    @staticmethod
    def create(conn, path: str)-> 'ImageMetadata':
        """--"""
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {ImageMetadata.TABLE_NAME} (path)
            VALUES (?)
        """, (path,))
        conn.commit()
        return ImageMetadata.read(conn, cursor.lastrowid)

    @staticmethod
    def read(conn, idx: int) -> 'ImageMetadata':
        """++"""
        cursor = conn.cursor()

        cursor.execute(f"{ImageMetadata.BASE_Q} where im.id = ?", (idx,))

        row = cursor.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    # @staticmethod
    # def update(conn, idx: int, image_metadata: 'ImageMetadata') -> 'int':
    #     cursor = conn.cursor()
    #     cursor.execute(f"""
    #         UPDATE {ImageMetadata.TABLE_NAME}
    #         SET path = ?, count = ?, time_spent = ?, facing = ?
    #         WHERE id = ?
    #     """, (*image_metadata.to_tuple(), idx))
    #     conn.commit()
    #     return cursor.rowcount

    # @staticmethod
    # def delete(conn, id) -> 'int':
    #     cursor = conn.cursor()
    #     cursor.execute(f"""
    #         DELETE FROM {ImageMetadata.TABLE_NAME}
    #         WHERE id = ?
    #     """, (id,))
    #     conn.commit()
    #     return cursor.rowcount

    # endregion CRUD

    # region Convenience

    @staticmethod
    def from_full_row(row) -> 'ImageMetadata':
        """++"""
        f = ImageMetadata.get_fields()
        return ImageMetadata(
            idx=row[f['id']],
            path=row[f['path_full']],
            path_id=row[f['path']],
            study_type=row[f['study_type_name']],
            study_type_id=row[f['study_type']],
            filename=row[f['filename']],
            last_viewed=row[f['last_viewed']],
            is_fav=row[f['fav']],

            count=row[f['count']],
            time_spent=row[f['time_spent']],
            diff=row[f['difficulty']],
            facing=row[f['facing']])

    @staticmethod
    def get_favs(conn, count: int = 10000, start: int = 0):
        """++"""
        c = conn.cursor()
        c.execute(f'{ImageMetadata.BASE_Q} WHERE im.fav = ? ORDER BY im.last_viewed DESC LIMIT ? OFFSET ?', (1, count, start))
        rows = c.fetchall()
        if rows is None:
            return None
        return [ImageMetadata.from_full_row(row) for row in rows]

    @staticmethod
    def get_last(conn, count: int = 60, start: int = 0):
        """++"""
        c = conn.cursor()
        c.execute(f'{ImageMetadata.BASE_Q} ORDER BY im.last_viewed DESC LIMIT ? OFFSET ?', (count, start))
        rows = c.fetchall()
        if rows is None:
            return None
        return [ImageMetadata.from_full_row(row) for row in rows]

    def get_by_id(conn, id: int):
        """++"""
        return ImageMetadata.read(conn, id)

    @staticmethod
    def get_by_path(conn, path) -> 'ImageMetadata':
        """++"""
        c = conn.cursor()
        c.execute(f"select id, filename from {ImageMetadata.TABLE_NAME} where filename = ?", (os.path.basename(path),))

        rows = c.fetchall()
        if len(rows) == 0:
            return None

        images = [ImageMetadata.read(conn, row[0]) for row in rows]
        target = [img for img in images if path == img.path]

        if len(target) == 0:
            return None

        if len(target) > 1:
            print(f"Found several images! ids:{[(' ' + img.id) for img in target]}")

        return target[0]

    # @staticmethod
    # def get_random_by_facing(conn, facing: int) -> 'ImageMetadata':
    #     c = conn.cursor()
    #     c.execute(f'SELECT * FROM {ImageMetadata.TABLE_NAME} WHERE facing = ? ORDER BY RANDOM() LIMIT 1', (facing,))
    #     row = c.fetchone()
    #     # print(str(row))
    #     if row is None:
    #         return None
    #     return ImageMetadata.from_full_row(row)

    @staticmethod
    def get_random_by_study_type(conn, study_type: int, same_folder: int = 0, prev_image_id: int = 1) -> 'ImageMetadata':
        """++"""
        c = conn.cursor()
        q_same_folder = ''
        if same_folder > 0:
            img = ImageMetadata.get_by_id(conn, prev_image_id)
            q_same_folder = f'AND im.path={img.path_id}'
        q = f'{ImageMetadata.BASE_Q} ' \
            f'WHERE im.study_type={study_type} {q_same_folder} ORDER BY RANDOM() LIMIT 1'
        c.execute(q)
        row = c.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)


    @staticmethod
    def set_image_fav(conn, image_id: int, is_fav: int):
        """++"""
        c = conn.cursor()
        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET fav = ? WHERE id = ? ', (is_fav, image_id))
        conn.commit()
        return c.rowcount > 0

    @staticmethod
    def set_image_last_viewed(conn, image_id: int, time: 'datetime'):
        """++"""
        c = conn.cursor()
        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET last_viewed = ? WHERE id = ?', (time, image_id))
        conn.commit()
        return c.rowcount > 0

    @staticmethod
    def get_id_by_path(conn, path: str) -> int:
        """++"""
        img = ImageMetadata.get_by_path(conn, path)
        if img is None:
            return -1
        return img.image_id

    @staticmethod
    def str_to_facing(facing: str) -> int:
        match facing:
            case "front":
                return 0
            case "side":
                return 1
            case "back":
                return 2
            case _:
                return 0

    @staticmethod
    def str_to_study_type(study_type: str) -> int:
        match study_type:
            case "academic":
                return 0
            case "pron":
                return 1
            case "any":
                return 2
            case _:
                return 0

    # endregion Convenience

    def to_html(self, timer=0) -> 'str':
        print("self.is_fav " + str(self.is_fav))
        with open('template.html', 'r') as f:
            template = Template(f.read())
        return template.substitute(
            image_id=self.image_id,
            path=self.path,
            count=self.count,
            time_spent=self.time_spent,
            study_type=self.study_type_id,
            facing=self.facing,
            timer=timer,
            difficulty=self.difficulty,
            is_fav=self.is_fav
        )

    def __str__(self):
        return f"{self.image_id}({self.last_viewed}): {self.path} fav({self.is_fav})"


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))

    db = sqlite3.connect(DB_FILE)
    ImageMetadata.static_initialize(db)
    print(ImageMetadata.read(db, 666))
    print(ImageMetadata.get_by_path(db, 'pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    print(ImageMetadata.get_id_by_path(db, 'pron\[Graphis] 2018-06-13 Gals – Asuna Kawai 河合あすな Natural beauty melons!\gra_asuna-k056.jpg'))
    print(ImageMetadata.read(db, 1666))
    print(ImageMetadata.read(db, 2666))

    print('random')
    print(ImageMetadata.get_random_by_study_type(db, 1))
    print(ImageMetadata.get_random_by_study_type(db, 1))
    print(ImageMetadata.get_random_by_study_type(db, 2, 1, 666))

    print('favs')
    for img in ImageMetadata.get_favs(db, count=2, start=3):
        print(img)

    print('last')
    for img in ImageMetadata.get_last(db, count=2, start=0):
        print(img)

