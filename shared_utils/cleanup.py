import os
from datetime import timedelta

from sqlalchemy import text, func, exists
from PIL import Image

from shared_utils.env import Env
from shared_utils.backup import make_database_backup
from app.models import Session
from app.models.models_lump import ImageMetadata, Path, BoardImage, Discover, ImageColor, ImageExtra, ImageTag


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


def cleanup_lost_videos_preview():
    """Remove .mp4.gif files for lost videos"""
    s = Session()

    lost = s.query(ImageMetadata).filter(ImageMetadata.lost == 1).all()

    print('Removing video previews...')

    for img in lost:
        if img.is_video and os.path.exists(img.path_abs):
            path = img.path_abs
            if not os.path.exists(path):
                continue
            print(f'Removing {path}...', end='')
            os.remove(path)
            print(f'\rRemoving {path}... Done')

    print('Removing video previews... Done')

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

    if auto_close:
        session.close()

    return count

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