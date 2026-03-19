import os

from sqlalchemy import func

from app.models import Session
from shared_utils.env import Env
from app.models.models_lump import ImageMetadata, Path
from shared_utils.backup import make_database_backup

from app.services.image_metadata_controller import ImageMetadataController as Ctrl

def mark_all_lost():
    print(f'Marking lost images...')
    make_database_backup(marker='mark_lost', force=True)

    s = Session()

    rows_max = s.query(func.count()).select_from(ImageMetadata).scalar()
    limit = 500
    offset = 0

    q = s.query(ImageMetadata)

    lost = []
    while True:
        images = q.limit(limit).offset(offset).all()
        offset += limit

        if len(images) == 0:
            break

        for image in images:
            image_path = image.path_abs

            if image.lost == 1:
                continue

            # video missing
            # removing trailing .gif to get real video path
            if image.is_video and not os.path.exists(image_path[:-4]):
                image.mark_as_lost(session=s, auto_commit=False)
                lost.append(image_path)
            # image missing
            elif not os.path.exists(image_path):
                image.mark_as_lost(session=s, auto_commit=False)
                lost.append(image_path)
        print(f'\r{int(offset / rows_max * 100)}%... Searching for lost images. Discovered {len(lost)}', end='')

    print(f'\n{len(lost)} lost images')
    [print(p) for p in lost]

    s.commit()
    s.close()

    print(f'Marking lost images... Done')



def relink_lost_images():
    """Try to relink by unique name"""
    make_database_backup(marker='relink_imgs', force=True)

    s = Session()

    lost = s.query(ImageMetadata).filter(ImageMetadata.lost == 1).all()
    found = []
    count = 0

    print('Trying to relink lost files.')

    print('Looking images that were mark lost but still exist...', end='')
    for img in lost:
        if not os.path.exists(img.path_abs):
            continue
        found.append((img.path_abs, "same"))
        lost.remove(img)
        count += 1
    print(f'\rLooking images that were mark lost but still exist... Done ({count})')

    s.flush()

    print('Looking for png to jpg conversion...', end='')
    count = 0
    png_to_jpg = [img for img in lost if img.filename.endswith('.png')]
    for img in png_to_jpg:
        # check if jpg version exists
        path = img.path_abs[:-3] + 'jpg'
        if not os.path.exists(path) or not os.path.isfile(path):
            continue
        # check if jpg not imported already
        fname = img.filename[:-3] + 'jpg'
        if s.query(ImageMetadata).filter(ImageMetadata.filename==fname, ImageMetadata.path_id == img.path_id).first() is not None:
            continue

        img.filename = fname
        img.mark_restored(session=s, auto_commit=False)
        found.append(("png",path))
        lost.remove(img)
        count += 1

    print(f'\rLooking for png to jpg conversion... Done ({count})')

    s.flush()

    print('Looking for folder change...')
    print('Collecting file names...', end='')
    Ctrl.update_paths_containing_images(session=s, auto_commit=False)
    files = {}
    paths = s.query(Path).all()
    count_max = len(paths)
    count = 0
    for p in paths:
        count += 1
        full_path = os.path.join(Env.IMAGES_PATH, p.path)
        if not os.path.exists(full_path):
            continue
        files[p.id] = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
        print(f'\r{int(count / count_max * 100)}% Collecting file names...', end='')

    print('\rCollecting file names... Done')

    count_max = len(lost)
    count = 0
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
    print(f'Currently lost images {len(lost) - len(found)}. Relinked {len(found)} images.')
    [print(f'Linked "{p[0]}" -> "{p[1]}"') for p in found]

    s.commit()
    s.close()