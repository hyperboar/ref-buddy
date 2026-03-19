import json
from datetime import datetime
import os
from PIL import Image
from sqlalchemy import func

from app.models.database_util import DatabaseUtil
from shared_utils.env import Env
from shared_utils.export_vid_gifs import ExportVidGifs
from shared_utils.gifextract import process_animation

from app.models import Session, get_engine
from app.models.models_lump import ImageMetadata, Path, ImageTag, Tag, ImageExtra
from shared_utils.nice_print import PrinterInterface


def create_new_db():
    DatabaseUtil.create_if_not_exist(get_engine())

def create_required_folders():
    required_paths = [
        Env.DB_PATH,
        Env.DB_BACKUP_PATH,
        Env.DRAWING_PATH,
        Env.THUMB_PATH,
        Env.TMP_PATH,
        Env.TMP_PATH_GIF,
        Env.IMAGES_PATH
    ]
    for path in required_paths:
        if not os.path.exists(path):
            os.makedirs(path)

    if not os.path.exists(Env.IMAGES_PATH):
        os.makedirs(os.path.join(Env.IMAGES_PATH, 'everything'))
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


def assign_folder_tags(start_at=None, session=None, printer:PrinterInterface=None):
    """Go over all imag_metadata rows and add tags academic, pron, the_bits, artists and frames(video)"""

    printer.line('Assigning essential tags to new images...', same_line=True)

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

    printer.line(f'Assigning essential tags to new images... Done', replace=True)
    printer.line('')

    printer.line(f'Assigning path tags...', same_line=True)

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

    printer.line(f'Assigning path tags... Done', replace=True)
    printer.line('')

    session.commit()

def assign_animation_tags(start_at=None, session=None, printer:PrinterInterface=None):
    printer.line('Assigning tags to animations and videos...', same_line=True)
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

    printer.line('Assigning tags to animations and videos... Done', replace=True)
    printer.line('')

def assign_video_extra_data(start_at=None, is_force=False, session=None, printer:PrinterInterface=None):
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

    printer.line(f'Assigning extra data for videos...', same_line=True)
    printer.step_up()
    while True:
        images = q.offset(offset).limit(limit).all()

        if len(images) == 0:
            break

        for image in images:
            i += 1
            if i % step == 0:
                printer.line(f'Assigning extra data for videos... {progress[int((i / step) % len(progress))]}', replace=True)

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

    printer.step_down()
    session.commit()

    printer.line(f'Assigning extra data for videos... Done', replace=True)
    printer.line('')

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

    # assign_video_extra_data(is_force=False)
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