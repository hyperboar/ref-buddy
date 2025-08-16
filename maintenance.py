import json
import math
from datetime import datetime, timedelta
import hashlib
import os
import shutil
from PIL import Image
from sqlalchemy import func, exists, text

from Env import Env
from export_vid_gifs import ExportVidGifs
from gifextract import process_animation
from image_metadata_controller import ImageMetadataController as Ctrl
from models.models_lump import Session, ImageMetadata, Path, ImageTag, ImageDupe, Tag, ImageExtra, BoardImage, Discover, \
    ImageColor, DatabaseUtil


def get_db_info():
    # if not os.path.isfile(Env.DB_FILE):
    #     print(f'Database file '{Env.DB_FILE}' does not exist.')
    #     return
    #
    # conn = sqlite3.connect(Env.DB_FILE)
    # cursor = conn.cursor()
    #
    # table = Ctrl.TABLE_NAME
    #
    # # Execute the query to check if the table exists
    # cursor.execute(f'SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'')
    #
    # # Get the result set and check if the table exists
    # result = cursor.fetchone()
    # if result:
    #     print(f'The '{table}' table exists.')
    # else:
    #     print(f'The '{table}' table does not exist.')
    #     cursor.close()
    #     conn.close()
    #     return
    #
    # cursor.execute(f'SELECT COUNT(*) FROM {ImageMetadata.TABLE_NAME}')
    # num_images = cursor.fetchone()[0]
    # print(f'Database file '{Env.DB_FILE}' exists and contains {num_images} images.')
    #
    # cursor.close()
    # conn.close()
    pass


def create_new_db():
    DatabaseUtil.create_if_not_exist()
    # make_database_backup(True)
    # if not os.path.isfile(Env.DB_FILE):
    #     print(f'Database file '{Env.DB_FILE}' do not exist. Creating one.')
    #
    # conn = sqlite3.connect(Env.DB_FILE)
    # cursor = conn.cursor()
    #
    # table = ImageMetadata.TABLE_NAME
    #
    # # Execute the query to check if the table exists
    # cursor.execute(f'SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'')
    # # Get the result set and check if the table exists
    # result = cursor.fetchone()
    # if result:
    #     print(f'The '{table}' table exists. Removing.')
    #     cursor.execute('DROP TABLE image_metadata')
    #
    # cursor.execute(ImageMetadata.get_table_schema())
    # print(f'New database created at path '{Env.DB_FILE}'.')
    #
    # cursor.close()
    # conn.close()
    pass

def create_required_folders():
    if not os.path.exists(Env.DB_PATH):
        os.makedirs(Env.DB_PATH)
    if not os.path.exists(Env.DB_BACKUP_PATH):
        os.makedirs(Env.DB_BACKUP_PATH)
    if not os.path.exists(Env.DRAWING_PATH):
        os.makedirs(Env.DRAWING_PATH)
    if not os.path.exists(Env.THUMB_PATH):
        os.makedirs(Env.THUMB_PATH)
    if not os.path.exists(Env.TMP_PATH):
        os.makedirs(Env.TMP_PATH)
    if not os.path.exists(Env.TMP_PATH_GIF):
        os.makedirs(Env.TMP_PATH_GIF)

    if not os.path.exists(Env.IMAGES_PATH):
        os.makedirs(Env.IMAGES_PATH)
        os.makedirs(os.path.join(Env.IMAGES_PATH, 'academic'))
        os.makedirs(os.path.join(Env.IMAGES_PATH, 'other'))
        with open(os.path.join(Env.IMAGES_PATH, 'put_images_into_sub_folders.txt'), 'w') as f:
            f.write('Images are supposed to be in sub folders.\nImages won\'t be imported when put into this directory!')

def generate_thumbs(start_at=None, session=None):
    # Create thumbnail folder if it doesn't exist
    if not os.path.exists(Env.THUMB_PATH):
        os.makedirs(Env.THUMB_PATH)

    if session is None:
        session = Session()

    if start_at is None:
        start_at = datetime.min

    max_i = (session.query(func.count()).select_from(ImageMetadata)
             .filter(ImageMetadata.lost == 0)
             .filter(ImageMetadata.imported_at > start_at)
             .scalar())
    limit = 500
    offset = 0

    i = 0
    i_step = 42
    new_count = 0

    broken_files = []

    q = (session.query(ImageMetadata)
         .filter(ImageMetadata.lost == 0)
         .filter(ImageMetadata.imported_at > start_at))


    print(f'0% Generating thumbs. {new_count} new', end='')
    while True:
        images = q.offset(offset).limit(limit).all()
        if len(images) == 0:
            break

        offset += limit


        # Generate thumbnail for each image
        for img in images:
            i += 1
            if (i % i_step) == 0:
                print(f'\r{int(i / max_i * 100.)}% Generating thumbs. {new_count} new', end='')
                # time.sleep(1)

            # Generate thumbnail filename by using id from database
            thumb_filename = os.path.join(Env.THUMB_PATH, f'{img.image_id}.jpg')

            # Skip image if thumbnail already exists
            if os.path.exists(thumb_filename):
                continue

            if not os.path.exists(img.path_abs):
                broken_files.append(img.path_abs)
                continue

            new_count += 1

            try:
                with Image.open(img.path_abs) as image:
                    image.thumbnail((Env.THUMB_MAX_SIZE, Env.THUMB_MAX_SIZE))

                    # Save thumbnail as JPEG file
                    image.convert('RGB').save(thumb_filename, 'JPEG')
            except:
                broken_files.append(img.path_abs)

    print(f'\r{int(i / max_i * 100.)}% Generating thumbs. {new_count} new... Done')
    if len(broken_files) > 0:
        print(f'{len(broken_files)} files had issues:')
        [print(p) for p in broken_files]


def rehash_images(rehash_all:bool):
    s = Session()

    rows_max = s.query(func.count()).select_from(ImageMetadata).filter(ImageMetadata.image_hash.is_(None)).scalar() if rehash_all else s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0

    q = s.query(ImageMetadata)

    print(f'0% Hashing images...', end='')
    while True:
        if rehash_all:
            images = q.offset(offset).limit(limit).all()
        else:
            images = q.filter(ImageMetadata.image_hash.is_(None)).limit(limit).all()

        if len(images) == 0:
            break

        for image in images:
            print(f'\r{int(offset/rows_max * 100)}% Hashing images {image.image_id} {image.path}', end='')
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

    print('\r100% Hashing images... Done' + (' ' * 50))

    # display duplicates
    # SELECT pa.path, A.filename, A.lost, pb.path, B.filename
    # FROM image_metadata AS A
    # JOIN image_metadata AS B ON A.hash = B.hash
    # JOIN paths as pa ON A.path = pa.id
    # JOIN paths as pb ON B.path = pb.id
    # WHERE A.path <> B.path AND A.lost <> 1 AND B.lost <> 1


def assign_folder_tags(start_at=None, session=None):
    """Go over all imag_metadata rows and add tags academic, pron, the_bits, artists and frames(video)"""

    print(f'Assigning essential tags to new images...', end='')

    if session is None:
        session = Session()

    # start_at currently does nothing here
    if start_at is None:
        start_at = datetime.min

    sub_paths = [
        ('academic', [2]), # tag academic
        ('pron', [3]), # tag pron
        ('the_bits', [3, 5]), # tag pron, the-bits
        ('artists', [4]), # tag 2d
        ('video', [6]), # tag frames
        ('doujin', [51]), # tag manga
    ]

    for sub_path, tags in sub_paths:
        paths = session.query(Path).filter(Path.path_raw.ilike(f'{sub_path}%')).all()
        p_ids = [p.id for p in paths]
        images = (session.query(ImageMetadata)
                  .filter(ImageMetadata.path_id.in_(p_ids))
                  .filter(ImageMetadata.imported_at > start_at)
                  .all())
        for im in images:
            for t in tags:
                session.merge(ImageTag(image_id=im.image_id, tag_id=t))

        session.flush()

    session.commit()

    print(f'\rAssigning essential tags to new images... Done')
    print(f'Assigning path tags...', end='')

    if session is None:
        session = Session()

    paths_all = session.query(Path).all()
    for p in paths_all:
        if len(p.tags) == 0:
            continue
        tags = [t.tag.id for t in p.tags]

        images = (session.query(ImageMetadata)
                  .filter(ImageMetadata.path_id == p.id)
                  .filter(ImageMetadata.imported_at > start_at).all())

        for im in images:
            for t in tags:
                session.merge(ImageTag(image_id=im.image_id, tag_id=t))

        session.flush()

    print(f'\rAssigning path tags... Done')

    session.commit()

def assign_animation_tags(start_at=None, session=None):
    print('Assigning tags to animations and videos...', end='')
    if session is None:
        session = Session()

    if start_at is None:
        start_at = datetime.min

    tag_anim = session.query(Tag).filter(Tag.tag == 'animated').first()
    tag_vid = session.query(Tag).filter(Tag.tag == 'video').first()


    if tag_anim is None:
        raise ValueError('Tag "animated" not found')
    if tag_vid is None:
        raise ValueError('Tag "video" not found')

    q = (session.query(ImageMetadata)
         .filter(ImageMetadata.lost == 0)
         .filter(ImageMetadata.imported_at > start_at))

    images = q.filter(ImageMetadata.filename.like('%.webp')).all() + \
             q.filter(ImageMetadata.filename.like('%.gif')).all()
    for im in images:
        st = ImageMetadata.source_type_by_path(im.path_abs)
        if st == 1:
            continue
        session.merge(ImageTag(image_id=im.image_id, tag_id=tag_anim.id))
        session.flush()

    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.filename.like('%.mp4.gif'))
              .filter(ImageMetadata.imported_at > start_at)
              .all())
    for im in images:
        st = ImageMetadata.source_type_by_path(im.path_abs)
        if st == 1:
            continue
        session.merge(ImageTag(image_id=im.image_id, tag_id=tag_vid.id))
        session.flush()

    session.commit()

    print('\rAssigning tags to animations and videos... Done', end='')

def remove_broken_video_gifs(session=None):
    if session is None:
        session = Session()

    images = session.query(ImageMetadata).filter(ImageMetadata.filename.like('%.mp4.gif')).all()

    broken_files = []

    for im in images:
        if not os.path.exists(im.path_abs):
            broken_files.append((im.path_abs, ''))
            continue

        try:
            with Image.open(im.path_abs) as image:
                image.thumbnail((Env.THUMB_MAX_SIZE, Env.THUMB_MAX_SIZE))

                # Save thumbnail as JPEG file
                image.convert('RGB')
        except:
            thumb_filename = os.path.join(Env.THUMB_PATH, f'{im.image_id}.jpg')
            broken_files.append((im.path_abs, thumb_filename))

    print(f'Found {len(broken_files)} broken files. Removing gif previews and thumbs...', end='')

    for fn, th in broken_files:
        if os.path.exists(fn):
            os.remove(fn)
        if os.path.exists(th):
            os.remove(th)

    print(f'\rFound {len(broken_files)} broken files. Removing gif previews and thumbs... Done')

def mark_all_lost():
    print(f'Marking lost images...')
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
        print(f'\r{int(offset / rows_max * 100)}%... Searching for lost images. {len(lost)} lost, {len(found)} found so far', end='')

    print(f'\n{len(lost)} lost images')
    [print(p) for p in lost]
    print(f'\nUnlost {len(found)} lost images')
    [print(p) for p in found]

    s.commit()
    s.close()

    print(f'Marking lost images... Done')

def cleanup_lost_images():
    make_database_backup(marker='cleanup_lost', force=True)

    print(f'Removing records about images that are lost...')

    session = Session()

    print(f'Marking lost for removal...', end='', flush=True)

    images = session.query(ImageMetadata).filter(ImageMetadata.lost == 1)
    ids = []
    for image in images:
        image.mark_removed(session=session, auto_commit=False)
        ids.append(image.image_id)

    session.commit()

    print(f'\rMarking lost for removal... Done', flush=True)

    print(f'Removing records about images that are lost... {len(ids)} images to remove)... ', end='', flush=True)
    count = remove_permanent(ids, session=session)
    session.close()

    print(f'\rRemoving records about images that are lost... Done. ({count} records removed)', flush=True)

def cleanup_image_thumbs():
    print(f'Cleaning up thumbs.')
    print(f'Collecting thumbs info...', end='', flush=True)

    ids = [int(os.path.splitext(f)[0]) for f in os.listdir(Env.THUMB_PATH) if os.path.isfile(os.path.join(Env.THUMB_PATH, f))]
    print(f'\rCollecting thumbs info... Done')

    s = Session()
    ids_to_remove = []
    count_max = len(ids)
    count = 0
    for i in ids:
        count += 1
        print(f'\r{int(count/count_max*100)}% Searching in database...', end='', flush=True)
        if s.query(exists().where(ImageMetadata.image_id == i)).scalar():
            continue
        ids_to_remove.append(i)

    print(f'\r{int(count / count_max * 100)}% Searching in database... Done')
    print(f'Appending images marked as "lost"...', end='', flush=True)

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

def remove_permanent(image_ids, session=None):
    auto_close = False
    if session is None:
        session = Session()
        auto_close = True

    images = (session.query(ImageMetadata)
              .filter(ImageMetadata.image_id.in_(image_ids))
              .filter(ImageMetadata.removed == 1)
              .all())

    if len(images) > 0:
        make_database_backup('before_perm_remove')

    count = 0
    for im in images:
        try:
            paths = [im.path_abs, os.path.join(Env.THUMB_PATH, str(im.image_id) + '.jpg')]
            if im.source_type_id == 3:  # video
                paths.append(im.path_abs[:-4])
            [os.remove(p) for p in paths if os.path.exists(p)]

            count += len(
                [session.delete(item) for item in session.query(BoardImage).filter(BoardImage.image_id == im.image_id)])
            count += len(
                [session.delete(item) for item in session.query(Discover).filter(Discover.image_id == im.image_id)])
            count += len(
                [session.delete(item) for item in session.query(ImageColor).filter(ImageColor.image_id == im.image_id)])
            count += len(
                [session.delete(item) for item in session.query(ImageExtra).filter(ImageExtra.image_id == im.image_id)])
            count += len(
                [session.delete(item) for item in session.query(ImageTag).filter(ImageTag.image_id == im.image_id)])
            session.delete(im)
            count += 1
            session.flush()
        except Exception as e:
            print(e)
            raise e

    session.commit()

    cleanup_paths(session)

    if auto_close:
        session.close()

    return count

def make_database_backup(marker:str='',force:bool=False):
    db_file = os.path.splitext(Env.DB_NAME)
    db_file_name = f'{db_file[0]}_'
    db_file_ext  = f'{db_file[1]}' if len(db_file) > 1 else ''
    time_fmt = '%Y-%m-%d_%H-%M'
    backup_interval = 60 * Env.DB_BACKUP_INTERVAL # seconds
    path = Env.DB_BACKUP_PATH

    if not os.path.exists(path):
        os.mkdir(path)

    if not os.path.exists(Env.DB_FILE):
        print(f'No existing database found.')
        return

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

def reassign_source_type_to_all():
    session = Session()
    q = session.query(ImageMetadata).filter(ImageMetadata.source_type_id == 0, ImageMetadata.lost == 0)

    offset = 0
    limit = 500
    while True:
        images = q.offset(offset).limit(limit).all()
        if len(images) == 0:
            break

        for im in images:
            if not os.path.exists(im.path_abs):
                im.lost = 1
                continue
            im.source_type_id = ImageMetadata.source_type_by_path(im.path_abs)
        session.flush()

    session.commit()

def collapse_import_times():
    session = Session()
    q = session.query(ImageMetadata)

    current_im = q.order_by(ImageMetadata.imported_at).first()
    interval = 5 * 60

    max_i = session.query(func.count()).select_from(ImageMetadata).scalar()
    i = 0

    make_database_backup('before_collapse_import_times' ,True)

    print(f'{i} checks passed. Last timestamp was {current_im.imported_at}', end='')
    while i < max_i:
        i += 1
        cur_time = current_im.imported_at
        cur_time_ts = cur_time.timestamp()
        start_time = cur_time - timedelta(seconds=1)
        end_time = cur_time   + timedelta(seconds=interval)
        images = q.filter(ImageMetadata.imported_at.between(start_time,end_time)).all()
        for im in images:
            if math.isclose(im.imported_at.timestamp(), cur_time_ts, rel_tol=1e-4, abs_tol=1e-4):
                continue
            im.imported_at = cur_time

        session.commit()

        print(f'\r{i} checks passed. Last timestamp was {cur_time}', end='')

        current_im = q.filter(ImageMetadata.imported_at > cur_time).order_by(ImageMetadata.imported_at).first()

        if current_im is None:
            break

    print(f'\r{i} checks passed. Last timestamp was {cur_time}... Done')

    session.close()

    make_database_backup('after_collapse_import_times', True)

def assign_video_extra_data(start_at=None, is_force=False, session=None):
    if session is None:
        session = Session()

    if start_at is None:
        start_at = datetime.min

    limit = 100
    offset = 0

    # videos only
    q = ((session.query(ImageMetadata)
         .filter(ImageMetadata.source_type_id == 3))
         .filter(ImageMetadata.imported_at > start_at))


    progress = ['/', '-', '\\', '|', ]
    i = 0
    step = 50

    print(f'Assigning extra data for videos...', end='', flush=True)
    while True:
        images = q.offset(offset).limit(limit).all()

        if len(images) == 0:
            break

        for image in images:
            i += 1
            if i % step == 0:
                print(f'\rAssigning extra data for videos... {progress[int((i / step) % len(progress))]}', end='', flush=True)

            if not is_force and len(image.extras) != 0:
                continue

            image_path = image.path_abs.replace('.mp4.gif', '.mp4')

            if not os.path.exists(image_path):
                image.mark_as_lost(session, auto_commit=False)
                continue

            dur, fps = ExportVidGifs.get_video_fps(image_path)
            data = {'dur': dur, 'fps': fps}

            if len(image.extras) == 0:
                session.merge(ImageExtra(image_id=image.image_id, data=json.dumps(data)))
            else:
                tmp = json.loads(image.extras[0].data)
                tmp['dur'] = data['dur']
                tmp['fps'] = data['fps']
                image.extras[0].data = json.dumps(tmp)

            session.flush()

            # print (f'{data} for {image.source_type_id}:{image.filename}')

        offset += limit

    session.commit()

    print(f'\rAssigning extra data for videos... Done' + (' ' * 50), flush=True)

def cleanup_paths(session=None):
    print(f'Cleanup paths...', end='', flush=True)
    if session is None:
        session = Session()

    paths = session.query(Path).all()
    for p in paths:
        im = session.get(ImageMetadata, p.preview)
        if im is not None: continue
        p.preview = 0
    session.flush()

    empty_paths = [p for p in paths if 0 == session.query(func.count()).select_from(ImageMetadata).filter(ImageMetadata.path_id == p.id).scalar()]

    for p in empty_paths:
        [session.delete(tag) for tag in p.tags]
        session.delete(p)
        session.flush()

    session.commit()
    print(f'\rCleanup paths... Done', flush=True)

def cleanup_vacuum(session=None):
    print(f'Vacuuming database...', end='', flush=True)
    if session is None:
        session = Session()

    session.execute(text("VACUUM"))
    print(f'\rVacuuming database... Done', flush=True)

def gif_split(force_all=True, session=None):
    if session is None:
        session = Session()

    if not os.path.exists(Env.TMP_PATH_GIF):
        os.makedirs(Env.TMP_PATH_GIF)

    print(f'Shredding gifs...', flush=True)

    gifs_q = (session.query(ImageMetadata)
            .filter(ImageMetadata.source_type_id == 2) # animated, not video
            .filter(ImageMetadata.filename.notlike('%.mp4.gif'))) # strictly speaking this one is not necessary

    if force_all:
        new_gifs = gifs_q
        max_count = gifs_q.count()
    else:
        new_gifs = []
        for gf in gifs_q:
            if os.path.exists(os.path.join(Env.TMP_PATH_GIF, gf.filename + '.json')): continue
            new_gifs.append(gf)

        max_count = len(new_gifs)

    count = 0
    for gf in new_gifs:
        count += 1
        print(f'\r({count}/{max_count}) Processing {gf.path_abs}{" " * 50}', end='', flush=True)
        process_animation(gf.path_abs, Env.TMP_PATH_GIF, {'image_id': gf.image_id})

    print(f'\nShredding gifs... Done ({count})', flush=True)

if __name__ == '__main__':
    # cleanup_lost_images()

    # reassign_source_type_to_all()
    # collapse_import_times()
    # assign_folder_tags()
    # assign_animation_tags()
    # remove_broken_video_gifs()

    assign_video_extra_data(is_force=False)
    pass
    # print(f'\rAssigning essential tags to new images...', end='')
    # mark_all_lost()
    # print(f'\rAssigning essential tags to new images... Done!', end='')

    # if len(sys.argv) > 1 and sys.argv[1] == '--new-db':
    #     create_new_db()
    # elif len(sys.argv) > 1 and sys.argv[1] == '--gen-thumb':
    #     generate_thumbs()
    # else:
    #     get_db_info()