import os
import sqlite3
import random
from string import Template

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

IMAGES_PATH = os.getenv('IMAGES_PATH')

class ImageMetadata:
    TABLE_NAME = "image_metadata"

    def __init__(self, path, count=0, time_spent=0, facing=0, last_viewed=0, idx=-1, diff='unknown'):
        self._path = path
        self._count = count
        self._time_spent = time_spent
        self._facing = facing
        self._last_viewed = last_viewed
        self._difficulty = diff
        self._id = idx

    @staticmethod
    def get_table_schema() -> str:
        return f"""
            CREATE TABLE IF NOT EXISTS {ImageMetadata.TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                facing INTEGER DEFAULT 0,
                last_viewed TIMESTAMP DEFAULT 0,
                difficulty INTEGER DEFAULT 10
            )
        """

    def save(self, conn):
        c = conn.cursor()
        c.execute(
            f"INSERT INTO {ImageMetadata.TABLE_NAME} (path, usage_count, time_spent_watching, facing, last_viewed) "
            f"VALUES (?, ?, ?, ?, ?)",
            (self.path, self.usage_count, self.time_spent_watching, self.facing, self.last_viewed)
        )
        conn.commit()

    def to_tuple(self):
        return (self.path, self.count, self.time_spent, self.facing)

    # region Getters

    @property
    def path(self):
        return self._path

    @property
    def count(self):
        return self._count

    @property
    def time_spent(self):
        return self._time_spent

    @property
    def facing(self):
        return self._facing

    @property
    def id(self):
        return self._facing

    @property
    def difficulty(self):
        return self._difficulty

    # endregion Getters

    # region CRUD

    @staticmethod
    def create(conn, path: str)-> 'ImageMetadata':
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {ImageMetadata.TABLE_NAME} (path)
            VALUES (?)
        """, (path,))
        conn.commit()
        return ImageMetadata.read(conn, cursor.lastrowid)

    @staticmethod
    def read(conn, idx: int) -> 'ImageMetadata':
        cursor = conn.cursor()
        cursor.execute(f" SELECT * FROM {ImageMetadata.TABLE_NAME} WHERE id = ? ", (idx,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    @staticmethod
    def update(conn, idx: int, image_metadata: 'ImageMetadata') -> 'int':
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE {ImageMetadata.TABLE_NAME}
            SET path = ?, count = ?, time_spent = ?, facing = ?
            WHERE id = ?
        """, (*image_metadata.to_tuple(), idx))
        conn.commit()
        return cursor.rowcount

    @staticmethod
    def delete(conn, id) -> 'int':
        cursor = conn.cursor()
        cursor.execute(f"""
            DELETE FROM {ImageMetadata.TABLE_NAME}
            WHERE id = ?
        """, (id,))
        conn.commit()
        return cursor.rowcount

    # endregion CRUD

    # region Convenience

    @staticmethod
    def from_full_row(row) -> 'ImageMetadata':
        return ImageMetadata(idx=row[0], path=row[1], count=row[2], time_spent=row[3], facing=row[4], last_viewed=row[5], diff=row[6])

    def get_by_id(conn, id: int):
        return ImageMetadata.read(conn, id)

    @staticmethod
    def get_by_path(conn, path) -> 'ImageMetadata':
        c = conn.cursor()
        c.execute(f'SELECT * FROM {ImageMetadata.TABLE_NAME} WHERE path = ?', (path,))
        row = c.fetchone()
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    @staticmethod
    def get_random_by_facing(conn, facing: int) -> 'ImageMetadata':
        c = conn.cursor()
        c.execute(f'SELECT * FROM {ImageMetadata.TABLE_NAME} WHERE facing = ? ORDER BY RANDOM() LIMIT 1', (facing,))
        row = c.fetchone()
        # print(str(row))
        if row is None:
            return None
        return ImageMetadata.from_full_row(row)

    @staticmethod
    def str_to_facing(facing: str) -> 'int':
        match facing:
            case "front":
                return 0
            case "side":
                return 1
            case "back":
                return 2
            case _:
                return 0

    # endregion Convenience

    def to_html(self, timer=0) -> 'str':
        with open('template.html', 'r') as f:
            template = Template(f.read())
        return template.substitute(
            image_id=self._id,
            path=self.path,
            count=self.count,
            time_spent=self.time_spent,
            facing=self.facing,
            timer=timer
        )
