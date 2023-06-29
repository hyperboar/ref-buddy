from datetime import datetime
import hashlib
import os
import shutil
import sqlite3
from PIL import Image
from sqlalchemy import func, exists

from Env import Env
from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Session, ImageMetadata, Path, ImageTag, ImageDupe


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
    # make_database_backup(True)
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
            images = q.offset(offset).limit(limit).all()
        else:
            images = q.filter(ImageMetadata.image_hash.is_(None)).limit(limit).all()

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
    make_database_backup(marker='mark_lost', force=True)

    s = Session()

    rows_max = s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0

    q = s.query(ImageMetadata)

    lost = []
    found = []
    while True:
        images = q.limit(limit).offset(offset).all()
        offset += limit

        if len(images) == 0:
            break

        for image in images:
            image_path = os.path.join(Env.IMAGES_PATH, image.path)

            if  image.lost == 1 and os.path.exists(image_path):
                image.lost = 0
                found.append(image_path)
            elif image.lost == 0 and not os.path.exists(image_path):
                image.mark_as_lost(session=s, auto_commit=False)
                lost.append(image_path)
        print(f"\r{int(offset / rows_max * 100)}%... Searching for lost images. {len(lost)} lost, {len(found)} found so far", end="")

    print(f"\n{len(lost)} lost images\n")
    [print(p) for p in lost]
    print(f"\nUnlost {len(found)} lost images\n")
    [print(p) for p in found]

    s.commit()
    s.close()

def cleanup_lost_images():
    cleanup_image_thumbs()

    make_database_backup(marker='cleanup_lost', force=True)

    print(f'Starting database cleanup.')

    s = Session()
    delete = lambda row: s.delete(row)
    subquery = s.query(ImageMetadata.image_id).filter(ImageMetadata.lost == 1).subquery()
    rows = s.query(ImageTag).join(subquery, ImageTag.image_id == subquery.c.image_id).all()
    print(f'Removing unused "tag" entries ({len(rows)})...', end='')
    list(map(delete, rows))
    s.flush()
    print(f'\rRemoving unused "tag" entries ({len(rows)})... Done')

    rows = s.query(ImageDupe).join(subquery, ImageDupe.image1 == subquery.c.image_id).all() +\
           s.query(ImageDupe).join(subquery, ImageDupe.image2 == subquery.c.image_id).all()
    print(f'Removing unused "duplicate" entries ({len(rows)})...', end='')
    list(map(delete, rows))
    s.flush()
    print(f'\rRemoving unused "duplicate" entries ({len(rows)})... Done')

    rows = s.query(ImageMetadata).filter(ImageMetadata.lost == 1).all()
    print(f'Removing "lost images" entries ({len(rows)})...', end='')
    list(map(delete, rows))
    s.flush()
    print(f'\rRemoving "lost images" entries ({len(rows)})... Done')

    s.commit()
    s.close()

    print(f'Database cleanup is done.')

def cleanup_image_thumbs():
    print(f'Cleaning up thumbs.')
    print(f'Collecting thumbs info...', end='')
    ids = [int(os.path.splitext(f)[0]) for f in os.listdir(Env.THUMB_PATH) if os.path.isfile(os.path.join(Env.THUMB_PATH, f))]
    print(f'\rCollecting thumbs info... Done')

    s = Session()
    ids_to_remove = []
    count_max = len(ids)
    count = 0
    for i in ids:
        count += 1
        print(f'\r{int(count/count_max*100)}% Searching in database...', end='')
        if s.query(exists().where(ImageMetadata.image_id == i)).scalar():
            continue
        ids_to_remove.append(i)

    print(f'\r{int(count / count_max * 100)}% Searching in database... Done')
    print(f'Appending images marked as "lost"...', end='')

    lost = s.query(ImageMetadata).filter(ImageMetadata.lost == 1).all()
    ids_to_remove += [l.image_id for l in lost if l.image_id in ids and l.image_id]
    print(f'\rAppending images marked as "lost"... Done')

    ids_to_remove = list(set(ids_to_remove))

    if len(ids_to_remove) == 0:
        print(f'Thumbs are already in a good shape! Nothing to delete!')
        return

    count_max = len(ids)
    count = 0
    for i in ids_to_remove:
        count += 1
        print(f'\r{int(count/count_max*100)}% Removing thumbs...', end='')
        try:
            os.remove(os.path.join(Env.THUMB_PATH, str(i) + '.jpg'))
        except FileNotFoundError:
            print(f'Something went wrong. Tried to remove file with name "' + str(i) + '.jpg' + '".')
    print(f'\r{int(count / count_max * 100)}% Removing thumbs... Done')

def relink_lost_images():
    """Try to relink by unique name"""
    make_database_backup(marker='relink_imgs', force=True)

    s = Session()

    lost = s.query(ImageMetadata).filter(ImageMetadata.lost == 1).all()
    print('Trying to relink lost files.')
    print('Collecting file names...', end='')
    Ctrl.update_paths_containing_images()
    files = {}
    paths = s.query(Path).all()
    count_max = len(paths)
    count = 0
    for p in paths:
        count += 1
        full_path = os.path.join(Env.IMAGES_PATH, p.path)
        files[p.id] = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
        print(f'\r{int(count / count_max * 100)}% Collecting file names...', end='')

    print('\rCollecting file names... Done')

    count_max = len(lost)
    count = 0
    found = []
    for l in lost:
        count += 1
        print(f'\r{int(count/count_max * 100)}% Searching for image lost from {l.path}', end='')

        names = s.query(ImageMetadata).filter(ImageMetadata.filename == l.filename).all()
        if len(names) > 1:
            # print(f'\nIN DATABASE More than 1 file for name {l.filename}. Found in:')
            # [print(f'{n.image_id}: {n.path}') for n in names]
            continue

        new_paths = [folder_id for folder_id in files if l.filename in files[folder_id]]

        if len(new_paths) == 1:
            old_path = l.path
            new_path = list(filter(lambda p: p.id == new_paths[0], paths))[0].path
            l.path_id = new_paths[0]
            l.lost = 0
            found.append((old_path, new_path))
        elif len(new_paths) > 1:
            print(f'\nMore than 1 file for name {l.filename}. Found in:')
            [print(f'{p}') for p in list(filter(lambda p: p.id in new_paths, paths))]


    print(f'\n')
    print(f'Currently lost images {len(lost) - len(found)}')
    print(f'Relinked images {len(found)}')
    [print(f'Linked "{p[0]}" to "{p[1]}"') for p in found]

    s.commit()
    s.close()

def make_database_backup(marker:str='',force:bool=False):
    db_file = os.path.splitext(Env.DB_NAME)
    db_file_name = f'{db_file[0]}_'
    db_file_ext  = f'{db_file[1]}' if len(db_file) > 1 else ''
    time_fmt = '%Y-%m-%d_%H-%M'
    backup_interval = 60 * Env.DB_BACKUP_INTERVAL # seconds
    path = Env.DB_BACKUP_PATH

    if not os.path.exists(path):
        os.mkdir(path)

    backup_files = [f for f in os.listdir(path) if f.startswith(db_file_name) and os.path.isfile(os.path.join(path, f))]
    start_pos = len(db_file_name)
    end_pos = start_pos + len(datetime.now().strftime(time_fmt))
    dates = [f[start_pos:end_pos] for f in backup_files]
    dates = sorted([datetime.strptime(d, time_fmt) for d in dates])

    if not force and \
            (len(dates) > 0 and datetime.now().timestamp() < (dates[-1].timestamp() + backup_interval)):
        return

    print(f'Backing up database. Found {len(backup_files)} backups, making new one.')

    if marker != '':
        marker = f'_{marker.lower().replace(" ", "_")}'
    backup_name = f'{db_file_name}{datetime.now().strftime(time_fmt)}{marker}{db_file_ext}'
    src = Env.DB_FILE
    dst = os.path.join(path, backup_name)
    shutil.copy(src, dst)

    backup_files += [backup_name]
    if len(backup_files) < Env.DB_BACKUP_MAX_COUNT:
        return

    backups = [(os.path.join(path, f), os.path.getctime(os.path.join(path, f))) for f in backup_files]
    backups = sorted(backups, key=lambda b: b[1])
    # print(f'{len(backups)} -> trim {len(backups) - Env.DB_BACKUP_MAX_COUNT}')
    # [print(p) for p in backups[:len(backups) - Env.DB_BACKUP_MAX_COUNT]]
    to_remove = backups[:len(backups) - Env.DB_BACKUP_MAX_COUNT]
    [os.remove(p[0]) for p in to_remove]


if __name__ == "__main__":
    cleanup_lost_images()
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