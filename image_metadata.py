import os
import sqlite3


class ImageMetadata:
    TABLE_NAME = "image_metadata"
    FIELDS = None
    BASE_Q = f"SELECT im.*, st.type AS study_type, pr.path AS path_full FROM image_metadata AS im JOIN study_types AS st ON im.study_type = st.id JOIN paths AS pr ON im.path = pr.id"

    def __init__(self, path, filename=None, count=0, last_viewed=0, idx=-1, rating=0, study_type=None, is_fav=0,
                 path_id=0, study_type_id=0, image_hash='', imported_at=0):
        self.image_id = idx
        self.path = os.path.join(study_type, path, filename)
        self.path_id = path_id
        self.study_type = study_type
        self.study_type_id = study_type_id
        self.last_viewed = last_viewed
        self.is_fav = is_fav
        self.rating = rating
        self.count = count

        self.image_hash = image_hash
        self.imported_at = imported_at

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
                path INTEGER NOT NULL,
                study_type INTEGER NOT NULL,
                fav INTEGER DEFAULT 0,
                count INTEGER DEFAULT 0,
                rating INTEGER DEFAULT 0,
                lost INTEGER DEFAULT 0,
                last_viewed TIMESTAMP DEFAULT '1999-01-01 00:00:00',
                imported_at TIMESTAMP DEFAULT (datetime('now')),
                hash TEXT,
                FOREIGN KEY (path) REFERENCES paths (id),
                FOREIGN KEY (study_type) REFERENCES study_types (id),
            );
            
            CREATE INDEX fn_index ON image_metadata (filename);
            
            CREATE TABLE IF NOT EXISTS paths (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS study_types (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL UNIQUE
            );
            
            INSERT INTO study_types (type) VALUES ('academic');
            INSERT INTO study_types (type) VALUES ('pron');
            INSERT INTO study_types (type) VALUES ('artists');
            INSERT INTO study_types (type) VALUES ('the_bits');
            INSERT INTO study_types (type) VALUES ('video');
        
            
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                tag TEXT UNIQUE
            );
            
            CREATE TABLE  IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (image_id) REFERENCES image_metadata(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (image_id, tag_id)
            );
            
            INSERT INTO tags (tag) VALUES ('futanari');
            
            INSERT INTO tags (tag) VALUES ('academic');
            INSERT INTO tags (tag) VALUES ('pron');
            INSERT INTO tags (tag) VALUES ('artists');
            INSERT INTO tags (tag) VALUES ('the_bits');
            Insert into tags (tag) values ('video');
            
            INSERT INTO tags (tag) VALUES ('face');
            
            INSERT INTO tags (tag) VALUES ('pose_stand');
            INSERT INTO tags (tag) VALUES ('pose_sit');
            INSERT INTO tags (tag) VALUES ('pose_lay');
            INSERT INTO tags (tag) VALUES ('pose_stand_bent');
            
            INSERT INTO tags (tag) VALUES ('view_body_front');
            INSERT INTO tags (tag) VALUES ('view_body_back');
            INSERT INTO tags (tag) VALUES ('view_body_side');
            INSERT INTO tags (tag) VALUES ('view_body_3-4');
            INSERT INTO tags (tag) VALUES ('view_body_top');
            INSERT INTO tags (tag) VALUES ('view_body_bottom');
            
            CREATE TABLE IF NOT EXISTS dupes (
                image1 INTEGER,
                image2 INTEGER,
                found_at TIMESTAMP DEFAULT (datetime('now')),
                fp INTEGER DEFAULT 0,
                r  INTEGER DEFAULT 0,
                PRIMARY KEY (image1_id, image2_id)
            );
        """

    # region CRUD

    @staticmethod
    def create(conn, path: str, study_types=None) -> 'ImageMetadata':
        c = conn.cursor()

        dir = os.path.dirname(path)
        file = os.path.basename(path)

        stype_list = [s for s in study_types if dir.startswith(s[1])]
        if stype_list is None or len(stype_list) == 0:
            print(f"Path '{path}' should be in study_type named folder (These: {','.join([s[1] for s in study_types])})")
            return -1

        stype = stype_list[0]
        new_path = dir[len(stype[1]) + 1:]

        c.execute(f"select * from paths where path = ?", (new_path,))
        rows = c.fetchone()
        if rows is None:
            c.execute(f"insert into paths (path) values (?)", (new_path,))
            path_id = c.lastrowid
        else:
            path_id = rows[0]

        # print(f"inserting {(path_id, stype[0], file)} for path '{new_path}'")
        c.execute(f"""
            INSERT INTO {ImageMetadata.TABLE_NAME} (path, study_type, filename, imported_at)
            VALUES (?, ?, ?, DATETIME('now'))
        """, (path_id, stype[0], file))
        conn.commit()
        return c.lastrowid

    @staticmethod
    def read(conn, idx: int) -> 'ImageMetadata':
        cursor = conn.cursor()

        cursor.execute(f"{ImageMetadata.BASE_Q} where im.id = {idx}")

        row = cursor.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    # endregion CRUD

    # region Convenience

    @staticmethod
    def from_full_row(row) -> 'ImageMetadata':
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
            rating=row[f['rating']],
            count=row[f['count']],
            image_hash=row[f['hash']],
            imported_at=row[f['imported_at']])

    @staticmethod
    def get_favs(conn, count: int = 10000, start: int = 0):
        c = conn.cursor()
        c.execute(f'{ImageMetadata.BASE_Q} WHERE im.fav = ? ORDER BY im.last_viewed DESC LIMIT ? OFFSET ?', (1, count, start))
        rows = c.fetchall()
        if rows is None:
            return None
        return [ImageMetadata.from_full_row(row) for row in rows]

    @staticmethod
    def get_last(conn, count: int = 60, start: int = 0):
        c = conn.cursor()
        c.execute(f'{ImageMetadata.BASE_Q} ORDER BY im.last_viewed DESC LIMIT ? OFFSET ?', (count, start))
        rows = c.fetchall()
        if rows is None:
            return None
        return [ImageMetadata.from_full_row(row) for row in rows]

    @staticmethod
    def get_by_id(conn, id: int):
        return ImageMetadata.read(conn, id)

    @staticmethod
    def get_by_path(conn, path) -> 'ImageMetadata':
        c = conn.cursor()
        c.execute(f"select id, filename from {ImageMetadata.TABLE_NAME} where filename = '{os.path.basename(path)}'")

        rows = c.fetchall()
        if len(rows) == 0:
            return None

        images = [ImageMetadata.read(conn, row[0]) for row in rows]
        target = [image for image in images if path == image.path]

        if len(target) == 0:
            return None

        if len(target) > 1:
            print(f"Found several images! ids:{[(' ' + img.id) for img in target]}")

        return target[0]

    @staticmethod
    def get_all_by_path_id(conn, path_id: int) -> '[ImageMetadata]':
        c = conn.cursor()

        c.execute(f"select path from paths where id = ?", (path_id,))
        row = c.fetchone()
        if row is None:
            return "", f"No path with id {path_id}", []

        c.execute(f"{ImageMetadata.BASE_Q} WHERE im.path = ?", (path_id,))

        rows = c.fetchall()
        if len(rows) == 0:
            return "", f"No images at path with id {path_id}", []

        images = [ImageMetadata.from_full_row(row) for row in rows]

        return images[0].study_type, row[0], images

    @staticmethod
    def get_all_by_tags(conn, tags: [int], limit=100, offset=0) -> '[ImageMetadata]':
        c = conn.cursor()

        tag_str = ','.join([str(num) for num in tags])
        # image ids
        c.execute(f"""
                SELECT image_id, COUNT(DISTINCT tag_id) AS tag_count
                FROM image_tags
                WHERE tag_id IN ({tag_str})
                GROUP BY image_id
            """)
        rows = c.fetchall()
        if len(rows) == 0:
            return f"No images found for tags ({tag_str}) in tags", []

        image_ids = [str(row[0]) for row in rows if row[1] == len(tags)]

        c.execute(f"{ImageMetadata.BASE_Q} WHERE im.id IN ({','.join(image_ids)}) ORDER BY im.imported_at  LIMIT {limit} OFFSET {offset}")

        rows = c.fetchall()
        if len(rows) == 0:
            return f"No images found for tags ({tag_str}) in images", []

        images = [ImageMetadata.from_full_row(row) for row in rows]

        return "", images

    @staticmethod
    def get_random_by_study_type(conn, study_type: int, same_folder: int = 0, prev_image_id: int = -1, min_rating=0) -> 'ImageMetadata':
        c = conn.cursor()
        q_same_folder = ''
        if same_folder > 0 and prev_image_id > 0:
            img = ImageMetadata.get_by_id(conn, prev_image_id)
            q_same_folder = f'AND im.path={img.path_id}' if img is not None and img.study_type_id == study_type else ''
        q = f'{ImageMetadata.BASE_Q} ' \
            f'WHERE im.study_type={study_type} {q_same_folder} AND im.rating >= {min_rating} ORDER BY RANDOM() LIMIT 1'
        c.execute(q)
        row = c.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    @staticmethod
    def set_image_fav(conn, image_id: int, is_fav: int):
        c = conn.cursor()
        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET fav = ? WHERE id = ? ', (is_fav, image_id))
        conn.commit()
        return c.rowcount > 0

    @staticmethod
    def add_image_rating(conn, image_id: int, rating_add: int, auto_commit=True) -> int:
        if rating_add == 0:
            return 1
        c = conn.cursor()
        c.execute(f'SELECT rating FROM {ImageMetadata.TABLE_NAME} WHERE id = ?', (image_id,))
        rating = c.fetchone()[0] + rating_add
        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET rating = ? WHERE id = ? ', (rating, image_id))
        if auto_commit:
            conn.commit()
            return rating if c.rowcount > 0 else 0
        else:
            return 0


    @staticmethod
    def set_image_last_viewed(conn, image_id: int, time: 'datetime'):
        c = conn.cursor()

        c.execute(f'SELECT count FROM {ImageMetadata.TABLE_NAME} WHERE id = ?', (image_id,))
        count = c.fetchone()[0] + 1

        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET last_viewed = ?, count = ? WHERE id = ?', (time, count, image_id))
        conn.commit()
        return c.rowcount > 0

    @staticmethod
    def get_id_by_path(conn, path: str) -> int:
        img = ImageMetadata.get_by_path(conn, path)
        if img is None:
            return -1
        return img.image_id

    @staticmethod
    def get_study_types(conn):
        c = conn.cursor()
        c.execute("select * from study_types")
        return c.fetchall()

    @staticmethod
    def get_all_tags(conn):
        c = conn.cursor()
        c.execute(f'SELECT * FROM tags')

        rows = c.fetchall()
        return rows #[row[1] row[1] for row in ]

    @staticmethod
    def get_tag_names(conn, tags: [int]):
        tag_rows = {str(tag[0]): tag[1] for tag in ImageMetadata.get_all_tags(conn)}

        tags_str = []
        for i in range(len(tags)):
            tags_str.append(tag_rows[str(tags[i])])

        return tags_str

    def mark_as_lost(self, conn, auto_commit=True):
        c = conn.cursor()
        c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET lost = 1 WHERE id = {self.image_id}')

        if auto_commit:
            conn.commit()

    def get_tags(self, conn):
        c = conn.cursor()
        c.execute(f'SELECT t.id, t.tag FROM image_tags it JOIN tags t ON it.tag_id = t.id WHERE it.image_id = {self.image_id} ORDER BY t.tag')

        rows = c.fetchall()
        return rows #[row[1] row[1] for row in ]

    # endregion Convenience

    def __str__(self):
        return f"{self.image_id}({self.last_viewed}): {self.path} fav({self.is_fav})"


if __name__ == "__main__":
    from Env import Env
    db = sqlite3.connect(Env.DB_FILE)
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
