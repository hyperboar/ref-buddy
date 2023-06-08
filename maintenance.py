import hashlib
import os
import sys
import sqlite3
from PIL import Image
from sqlalchemy import func
from sqlalchemy.dialects.sqlite import insert

from image_metadata_controller import ImageMetadataController as Ctrl
from Env import Env
from models.models_lump import Session, ImageMetadata, ImageTag, engine


def get_db_info():
    # if not os.path.isfile(Env.DB_FILE):
    #     print(f"Database file '{Env.DB_FILE}' does not exist.")
    #     return
    #
    # conn = sqlite3.connect(Env.DB_FILE)
    # cursor = conn.cursor()
    #
    # table = Ctrl.TABLE_NAME
    #
    # # Execute the query to check if the table exists
    # cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    #
    # # Get the result set and check if the table exists
    # result = cursor.fetchone()
    # if result:
    #     print(f"The '{table}' table exists.")
    # else:
    #     print(f"The '{table}' table does not exist.")
    #     cursor.close()
    #     conn.close()
    #     return
    #
    # cursor.execute(f"SELECT COUNT(*) FROM {ImageMetadata.TABLE_NAME}")
    # num_images = cursor.fetchone()[0]
    # print(f"Database file '{Env.DB_FILE}' exists and contains {num_images} images.")
    #
    # cursor.close()
    # conn.close()
    pass


def create_new_db():
    # if not os.path.isfile(Env.DB_FILE):
    #     print(f"Database file '{Env.DB_FILE}' do not exist. Creating one.")
    #
    # conn = sqlite3.connect(Env.DB_FILE)
    # cursor = conn.cursor()
    #
    # table = ImageMetadata.TABLE_NAME
    #
    # # Execute the query to check if the table exists
    # cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    # # Get the result set and check if the table exists
    # result = cursor.fetchone()
    # if result:
    #     print(f"The '{table}' table exists. Removing.")
    #     cursor.execute('DROP TABLE image_metadata')
    #
    # cursor.execute(ImageMetadata.get_table_schema())
    # print(f"New database created at path '{Env.DB_FILE}'.")
    #
    # cursor.close()
    # conn.close()
    pass

def generate_thumbs():
    # Create thumbnail folder if it doesn't exist
    if not os.path.exists(Env.THUMB_PATH):
        os.makedirs(Env.THUMB_PATH)

    s = Session()

    max_i = s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0

    i = 0
    i_step = 42
    new_count = 0

    while True:
        images = s.query(ImageMetadata).limit(limit).offset(offset).all()
        if len(images) == 0:
            break

        offset += limit

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

        print(f"\rProgress: {int(i / max_i * 100.)}% ({new_count} new)", end='')


def rehash_images(rehash_all):
    s = Session()

    rows_max = s.query(func.count()).select_from(ImageMetadata).filter(ImageMetadata.image_hash.is_(None)).scalar() if rehash_all else s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0

    q = s.query(ImageMetadata)

    while True:
        if rehash_all:
            images = q.limit(limit).offset(offset).all()
        else:
            images = q.filter(ImageMetadata.image_hash.is_(None)).limit(limit).offset(offset).all()

        if len(images) == 0:
            break

        for image in images:
            print(f"\r{int(offset/rows_max * 100)}%... Hashing {image.image_id} {image.path}", end="")
            image_path = os.path.join(Env.IMAGES_PATH, image.path)

            if not os.path.exists(image_path):
                image.mark_as_lost(s, auto_commit=False)
                continue

            with open(image_path, 'rb') as file:
                image_data = file.read()
            image.image_hash = hashlib.sha1(image_data).hexdigest()
            s.flush()

        offset += limit

    s.commit()

    print("\r100% Rehashing complete", end="")

    # display duplicates
    # SELECT pa.path, A.filename, A.lost, pb.path, B.filename
    # FROM image_metadata AS A
    # JOIN image_metadata AS B ON A.hash = B.hash
    # JOIN paths as pa ON A.path = pa.id
    # JOIN paths as pb ON B.path = pb.id
    # WHERE A.path <> B.path AND A.lost <> 1 AND B.lost <> 1


def assign_folder_tags():
    """Go over all imag_metadata rows and add tags academic, pron, the_bits, artists and frames(video)"""

    conn = sqlite3.connect(Env.DB_FILE)

    c = conn.cursor()
    c.execute("""
        -- academic
        INSERT OR IGNORE INTO image_tags (image_id, tag_id)
        SELECT id, 2
        FROM image_metadata
        WHERE study_type = 1;
    """)
    c.execute(f"""
        -- pron and the-bits
        INSERT OR IGNORE INTO image_tags (image_id, tag_id)
        SELECT id, 3
        FROM image_metadata
        WHERE study_type in (2, 4);
    """)
    c.execute(f"""
        -- the_bits
        INSERT OR IGNORE INTO image_tags (image_id, tag_id)
        SELECT id, 5
        FROM image_metadata
        WHERE study_type = 4;
    """)
    c.execute(f"""
        -- artists
        INSERT OR IGNORE INTO image_tags (image_id, tag_id)
        SELECT id, 4
        FROM image_metadata
        WHERE study_type = 3;
    """)
    c.execute(f"""
        -- frames
        INSERT OR IGNORE INTO image_tags (image_id, tag_id)
        SELECT id, 6
        FROM image_metadata
        WHERE study_type = 5;
    """)

    conn.commit()
    conn.close()

def mark_all_lost():
    s = Session()

    rows_max = s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0
    lost_count = 0

    q = s.query(ImageMetadata)

    while True:
        images = q.limit(limit).offset(offset).all()
        offset += limit

        if len(images) == 0:
            break

        for image in images:
            image_path = os.path.join(Env.IMAGES_PATH, image.path)

            if os.path.exists(image_path):
                continue

            lost_count += 1
            print(f"\nLost {image.image_id} {image.path}")
            image.mark_as_lost(session=s, auto_commit=False)

        print(f"\r{int(offset / rows_max * 100)}%... Searching for lost images. Found {lost_count} lost so far", end="")

    if lost_count > 0:
        print(f"\nFound {lost_count} lost images\n")
        s.commit()
    else:
        print(f"\nNothing lost yet!\n")


def cleanup_lost_images():
    pass


if __name__ == "__main__":
    pass
    # print(f"\rAssigning essential tags to new images...", end="")
    # mark_all_lost()
    # print(f"\rAssigning essential tags to new images... Done!", end="")

    # if len(sys.argv) > 1 and sys.argv[1] == "--new-db":
    #     create_new_db()
    # elif len(sys.argv) > 1 and sys.argv[1] == "--gen-thumb":
    #     generate_thumbs()
    # else:
    #     get_db_info()