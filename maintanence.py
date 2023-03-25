import os
import sys
import sqlite3
from image_metadata import ImageMetadata
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the values of DB_PATH and DB_NAME from the environment
DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))

def get_db_info():
    if not os.path.isfile(DB_FILE):
        print(f"Database file '{DB_FILE}' does not exist.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    table = ImageMetadata.TABLE_NAME

    # Execute the query to check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")

    # Get the result set and check if the table exists
    result = cursor.fetchone()
    if result:
        print(f"The '{table}' table exists.")
    else:
        print(f"The '{table}' table does not exist.")
        cursor.close()
        conn.close()
        return

    cursor.execute(f"SELECT COUNT(*) FROM {ImageMetadata.TABLE_NAME}")
    num_images = cursor.fetchone()[0]
    print(f"Database file '{DB_FILE}' exists and contains {num_images} images.")

    cursor.close()
    conn.close()


def create_new_db():
    if not os.path.isfile(DB_FILE):
        print(f"Database file '{DB_FILE}' do not exist. Creating one.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    table = ImageMetadata.TABLE_NAME

    # Execute the query to check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    # Get the result set and check if the table exists
    result = cursor.fetchone()
    if result:
        print(f"The '{table}' table exists. Removing.")
        cursor.execute('DROP TABLE image_metadata')

    cursor.execute(ImageMetadata.get_table_schema())
    print(f"New database created at path '{DB_FILE}'.")

    cursor.close()
    conn.close()

def create_new_db():
    if not os.path.isfile(DB_FILE):
        print(f"Database file '{DB_FILE}' do not exist. Creating one.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    table = ImageMetadata.TABLE_NAME

    # Execute the query to check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    # Get the result set and check if the table exists
    result = cursor.fetchone()
    if result:
        print(f"The '{table}' table exists. Removing.")
        cursor.execute('DROP TABLE image_metadata')

    cursor.execute(ImageMetadata.get_table_schema())
    print(f"New database created at path '{DB_FILE}'.")

    cursor.close()
    conn.close()

def migrate_db():
    if not os.path.isfile(DB_FILE):
        print(f"Database file '{DB_FILE}' do not exist. Can't migrate.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    table = ImageMetadata.TABLE_NAME

    # Execute the query to check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    # Get the result set and check if the table exists
    result = cursor.fetchone()
    if not result:
        print(f"The '{table}' table exists. Removing.")

    # m = f"""
    # ALTER TABLE {table}
    # ADD COLUMN difficulty TEXT DEFAULT 'unknown';
    # """
    # cursor.execute(m)
    print(f"Database migrated successfully!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--new-db":
        create_new_db()
    elif len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        migrate_db()
    else:
        get_db_info()