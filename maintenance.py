import hashlib
import os
import sys
import sqlite3
from PIL import Image
from image_metadata import ImageMetadata
import time
from Env import Env


def get_db_info():
    if not os.path.isfile(Env.DB_FILE):
        print(f"Database file '{Env.DB_FILE}' does not exist.")
        return

    conn = sqlite3.connect(Env.DB_FILE)
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
    print(f"Database file '{Env.DB_FILE}' exists and contains {num_images} images.")

    cursor.close()
    conn.close()


def create_new_db():
    if not os.path.isfile(Env.DB_FILE):
        print(f"Database file '{Env.DB_FILE}' do not exist. Creating one.")

    conn = sqlite3.connect(Env.DB_FILE)
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
    print(f"New database created at path '{Env.DB_FILE}'.")

    cursor.close()
    conn.close()


def create_new_db():
    if not os.path.isfile(Env.DB_FILE):
        print(f"Database file '{Env.DB_FILE}' do not exist. Creating one.")

    conn = sqlite3.connect(Env.DB_FILE)
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
    print(f"New database created at path '{Env.DB_FILE}'.")

    cursor.close()
    conn.close()


def generate_thumbs():
    # Connect to SQLite database
    conn = sqlite3.connect(Env.DB_FILE)

    ImageMetadata.static_initialize(conn)

    # Select all image paths from image_metadata table
    # c.execute(f"SELECT id, path FROM {ImageMetadata.TABLE_NAME}")
    c = conn.cursor()
    c.execute(ImageMetadata.BASE_Q)
    images = [ImageMetadata.from_full_row(row) for row in  c.fetchall()]

    # Create thumbnail folder if it doesn't exist
    if not os.path.exists(Env.THUMB_PATH):
        os.makedirs(Env.THUMB_PATH)

    i = 0
    i_step = 42
    max_i = len(images)
    new_count = 0
    # Generate thumbnail for each image
    for img in images:

        i += 1
        if (i % i_step) == 0:
            print(f"\rProgress: {int(i / max_i * 100.)}% ({new_count} new)", end='')
            # time.sleep(1)

        # Generate thumbnail filename by using id from database
        thumb_filename = os.path.join(Env.THUMB_PATH, f"{img.image_id}.jpg")

        # Skip image if thumbnail already exists
        if os.path.exists(thumb_filename):
            continue

        new_count += 1

        path = os.path.join(Env.IMAGES_PATH, img.path)

        # Load image and generate thumbnail
        image = Image.open(path)
        image.thumbnail((Env.THUMB_MAX_SIZE, Env.THUMB_MAX_SIZE))

        # Save thumbnail as JPEG file
        image.convert('RGB').save(thumb_filename, 'JPEG')

        if i > max_i:
            break

    print(f"\rProgress: {int(i / max_i * 100.)}%", end='')
    # Close database connection
    conn.close()


def rehash_images():
    conn = sqlite3.connect(Env.DB_FILE)

    ImageMetadata.static_initialize(conn)

    c = conn.cursor()
    # rows count
    c.execute(f"SELECT COUNT(*) FROM {ImageMetadata.TABLE_NAME}")

    rows_max = c.fetchone()[0]
    rows_step = 500
    rows_start = 0

    while rows_start < rows_max:
        c.execute(f"{ImageMetadata.BASE_Q} LIMIT {rows_step} OFFSET {rows_start}")
        images = [ImageMetadata.from_full_row(row) for row in c.fetchall()]

        for image in images:
            print(f"\r{int(rows_start/rows_max * 100)}%... Hashing {image.image_id} {image.path}", end="")

            image_path = os.path.join(Env.IMAGES_PATH, image.path)

            if not os.path.exists(image_path):
                image.mark_as_lost(conn, auto_commit=False)
                continue

            with open(image_path, 'rb') as file:
                image_data = file.read()
            image_hash = hashlib.sha1(image_data).hexdigest()

            c.execute(f'UPDATE {ImageMetadata.TABLE_NAME} SET hash = "{image_hash}" WHERE id = {image.image_id}')


        rows_start += rows_step

    conn.commit()
    conn.close()

    print("\r100% Rehashing complete", end="")

    # display duplicates
    # SELECT pa.path, A.filename, A.lost, pb.path, B.filename
    # FROM image_metadata AS A
    # JOIN image_metadata AS B ON A.hash = B.hash
    # JOIN paths as pa ON A.path = pa.id
    # JOIN paths as pb ON B.path = pb.id
    # WHERE A.path <> B.path AND A.lost <> 1 AND B.lost <> 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--new-db":
        create_new_db()
    elif len(sys.argv) > 1 and sys.argv[1] == "--gen-thumb":
        generate_thumbs()
    else:
        get_db_info()