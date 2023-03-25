from datetime import datetime
import random
import sqlite3
from string import Template


class ImageMetadata:
    TABLE_NAME = 'image_metadata'

    def __init__(self, path, usage_count=0, time_spent_watching=0, facing='front', last_viewed=None):
        self.path = path
        self.usage_count = usage_count
        self.time_spent_watching = time_spent_watching
        self.facing = facing
        self.last_viewed = last_viewed

    def save(self):
        conn = sqlite3.connect('metadata.db')
        c = conn.cursor()
        c.execute(
            f"INSERT INTO {ImageMetadata.TABLE_NAME} (path, usage_count, time_spent_watching, facing, last_viewed) "
            f"VALUES (?, ?, ?, ?, ?)",
            (self.path, self.usage_count, self.time_spent_watching, self.facing, self.last_viewed)
        )
        conn.commit()
        conn.close()

    @classmethod
    def get_table_schema(cls):
        return f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                usage_count INTEGER NOT NULL DEFAULT 0,
                time_spent_watching INTEGER NOT NULL DEFAULT 0,
                facing TEXT NOT NULL DEFAULT 'front',
                last_viewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

    @classmethod
    def get_by_path(cls, path):
        conn = sqlite3.connect('metadata.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM {cls.TABLE_NAME} WHERE path=?", (path,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return None
        return cls(*row[1:])

    @classmethod
    def get_random_by_facing(cls, facing):
        conn = sqlite3.connect('metadata.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM {cls.TABLE_NAME} WHERE facing=?", (facing,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            return None
        return cls(*random.choice(rows)[1:])

    def increment_count_and_update_last_viewed(self):
        self.usage_count += 1
        self.last_viewed = datetime.now()
        conn = sqlite3.connect('metadata.db')
        c = conn.cursor()
        c.execute(f"UPDATE {ImageMetadata.TABLE_NAME} SET usage_count=?, last_viewed=? WHERE id=?",
                  (self.usage_count, self.last_viewed, self.id))
        conn.commit()
        conn.close()

    def to_html(self):
        template = Template("""
            <html>
                <head>
                    <title>{{ path }}</title>
                </head>
                <body>
                    <img src="{{ path }}" alt="{{ path }}">
                    <br>
                    <button onclick="incrementCount('{{ id }}')">Increment Count</button>
                    <script>
                        function incrementCount(id) {
                            fetch(`/increment_count/${id}`)
                        }
                    </script>
                </body>
            </html>
        """)
        return template.substitute(path=self.path, id=self.id)