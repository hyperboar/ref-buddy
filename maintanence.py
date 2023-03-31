import os
import sys
import sqlite3
from PIL import Image
from image_metadata import ImageMetadata
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Get the values of DB_PATH and DB_NAME from the environment
DB_FILE = os.path.join(os.getenv('DB_PATH'), os.getenv('DB_NAME'))
IMAGES_PATH = os.getenv('IMAGES_PATH')
THUMB_PATH = os.getenv('THUMB_PATH')
THUMB_MAX_SIZE = int(os.getenv('THUMB_MAX_SIZE'))


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


def generate_thumbs():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Select all image paths from image_metadata table
    c.execute(f"SELECT id, path FROM {ImageMetadata.TABLE_NAME}")
    results = c.fetchall()

    # Create thumbnail folder if it doesn't exist
    if not os.path.exists(THUMB_PATH):
        os.makedirs(THUMB_PATH)

    i = 0
    i_step = 42
    max_i = len(results)
    new_count = 0
    # Generate thumbnail for each image
    for image_id, path in results:

        i += 1
        if (i % i_step) == 0:
            print(f"\rProgress: {int(i / max_i * 100.)}% ({new_count} new)", end='')
            time.sleep(1)

        # Generate thumbnail filename by using id from database
        thumb_filename = os.path.join(THUMB_PATH, f"{image_id}.jpg")

        # Skip image if thumbnail already exists
        if os.path.exists(thumb_filename):
            continue

        new_count += 1

        path = os.path.join(IMAGES_PATH, path)

        # Load image and generate thumbnail
        image = Image.open(path)
        image.thumbnail((THUMB_MAX_SIZE, THUMB_MAX_SIZE))

        # Save thumbnail as JPEG file
        image.convert('RGB').save(thumb_filename, 'JPEG')

        if i > max_i:
            break

    print(f"\rProgress: {int(i / max_i * 100.)}%", end='')
    # Close database connection
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--new-db":
        create_new_db()
    elif len(sys.argv) > 1 and sys.argv[1] == "--gen-thumb":
        generate_thumbs()
    else:
        get_db_info()