import os.path
from itertools import combinations

from flask import Blueprint, request, render_template_string, render_template
from PIL import Image

from Env import Env
from models.models_lump import Session, ImageDupe, ImageMetadata, ImageTag
from server_args_helpers import get_arg, Args

routes_dupes = Blueprint('routes_dupes', __name__)

@routes_dupes.route('/dupes')
def view_dupes():
    s = Session()

    limit = 500
    offset = 0
    get_rows = lambda l, o: s.query(ImageDupe).filter(ImageDupe.resolved == 0, ImageDupe.false_positive == 0).offset(o).limit(l).all()
    rows = get_rows(limit, offset)

    dupes = []

    while len(rows) > 0:
        for d in rows:
            dupes.append((d.image1, d.image2))

        offset += limit
        rows = get_rows(limit, offset)

    dupes = list(sorted(dupes, key=lambda item: item[0]))

    print(len(dupes))

    return render_template('tpl_view_dupes.html', dupes=dupes)

@routes_dupes.route('/dupes-resolve-pick-largest')
def pick_largest_and_resolve():
    ids = get_arg(request.args, Args.mult_image_ids)

    session = Session()

    images = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(ids)).all()

    for im in images:
        path = os.path.join(Env.IMAGES_PATH, im.path)
        if not os.path.exists(path):
            im.size = (0,0)
        else:
            with Image.open(path) as image:
                im.size = image.size

    images = sorted(images, key=lambda im:(-im.size[0], im.imported_at))

    print('Resolve')
    [print(f'{im.image_id}: {im.size[0]}x{im.size[1]} {im.imported_at} -> {im.path}') for im in images]

    masters = [images[0].image_id] # first oldest image with highest resolution
    clones = [id for id in ids if id not in masters]

    # print(f'm {masters}')
    # print(f'c {clones}')

    try:
        sync_tags(masters=masters, clones=clones, session=session)
        sync_image_metadata(masters=masters, clones=clones, session=session)
        remove_clones(clones=clones, session=session)

        session.commit()
    except:
        session.rollback()
        raise

    session.close()

    return render_template_string('ok')

@routes_dupes.route('/dupes-not-same')
def mark_not_same():
    ids = get_arg(request.args, Args.mult_image_ids)
    session = Session()

    try:
        dupes = []
        combs = list(combinations(ids, 2))
        for comb in combs:
            dupes += session.query(ImageDupe).filter(ImageDupe.image1 == comb[0], ImageDupe.image2 == comb[1]).all()

        for d in dupes:
            d.false_positive = 1

        session.commit()

        print(f'Mark not same. {len(combs)} combinations ({len(dupes)} rows)')
        print(f'ids {ids}')
        [print(f'{im.image1} -> {im.image2}') for im in dupes]
    except:
        session.rollback()
        raise
    session.close()

    return render_template_string('ok')

@routes_dupes.route('/dupes-remove')
def mark_just_remove():
    ids = get_arg(request.args, Args.mult_image_ids)
    session = Session()

    sync_tags(ids, session=session)

    session.rollback()

    # # remove files
    # paths = [os.path.join(Env.IMAGES_PATH, im.path) for im in images]
    # for p in paths:
    #     if not os.path.exists(p):
    #         continue
    #     os.remove(p)

    print('Just remove')
    # [print(f'{im.path}') for im in images]


    return render_template_string('ok')

# def sync_images(master:[int], clones:[int], session=None):
#     if session is None:
#         session = Session
#
#     images = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(clones)).all()
#
#     for im in images:
#         rows = session.query(ImageDupe).filter(ImageDupe.image1 == im.image_id).all() + \
#                session.query(ImageDupe).filter(ImageDupe.image2 == im.image_id).all()
#         dupes = {}
#
#     # remove tags and dupes records
#     for im in images:
#         rows = session.query(ImageDupe).filter(ImageDupe.image1 == im.image_id).all() + \
#                session.query(ImageDupe).filter(ImageDupe.image2 == im.image_id).all() + \
#                session.query(ImageTag).filter(ImageTag.image_id == im.image_id).all()
#         [session.delete(row) for row in rows]
#
#     session.flush()

def sync_image_metadata(clones: [int], masters: [int], session=None):
    auto_commit = False
    if session is None:
        auto_commit = True
        session = Session

    # get tags

    # tmp_m = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(masters)).all()
    # tmp_c = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(clones)).all()
    # print('before')
    # [print('m ' + str(im)) for im in tmp_m]
    # [print('c ' + str(im)) for im in tmp_c]
    # print('end before')

    for clone in clones:
        if masters is None:
            masters = get_masters([clone], session=session)

        m_rows = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(masters)).all()
        c_rows = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_([clone])).all()

        for c_row in c_rows:
            for m_row in m_rows:
                m_row.lost = 0
                m_row.count  += c_row.count
                m_row.rating += c_row.rating
                m_row.fav = max(m_row.fav, c_row.fav)
                m_row.last_viewed = max(m_row.last_viewed, c_row.last_viewed)

    # print('after')
    # [print('m ' + str(im)) for im in tmp_m]
    # [print('c ' + str(im)) for im in tmp_c]
    # print('end after')

    if auto_commit:
        session.commit()
    else:
        session.flush()

def sync_tags(clones:[int], masters:[int]=None, session=None):
    auto_commit = False
    if session is None:
        auto_commit = True
        session = Session

    for clone in clones:
        if masters is None:
            masters = get_masters([clone], session=session)

        # print(f'for clone {clone}:')
        # print('master')
        # [print(m) for m in masters]

        # get tags
        image_tags = session.query(ImageTag).filter(ImageTag.image_id.in_([clone])).all()
        tags = []
        for t in image_tags:
            if t in tags:
                continue
            tags.append(t.tag_id)

        for im in masters:
            for t in tags:
                session.merge(ImageTag(image_id=im, tag_id=t))

    if auto_commit:
        session.commit()
    else:
        session.flush()

    # for im in images:
    #     rows = session.query(ImageDupe).filter(ImageDupe.image1 == im.image_id).all() + \
    #            session.query(ImageDupe).filter(ImageDupe.image2 == im.image_id).all()
    #     dupes = {}

    # # remove tags and dupes records
    # for im in images:
    #     rows = session.query(ImageDupe).filter(ImageDupe.image1 == im.image_id).all() + \
    #            session.query(ImageDupe).filter(ImageDupe.image2 == im.image_id).all() + \
    #            session.query(ImageTag).filter(ImageTag.image_id == im.image_id).all()
    #     [session.delete(row) for row in rows]

def remove_clones(clones:[int], session=None):
    auto_commit = False
    if session is None:
        auto_commit = True
        session = Session

    remove_rows_count = 0
    update_rows_count = 0
    for im in clones:
        # purge tags
        rows = session.query(ImageTag).filter(ImageTag.image_id == im).all()
        [session.delete(row) for row in rows]
        remove_rows_count += len(rows)

        # mark dupe resolved
        rows = session.query(ImageDupe).filter(ImageDupe.image1 == im).all() + \
               session.query(ImageDupe).filter(ImageDupe.image2 == im).all()
        for row in rows:
            row.resolved = 1
        update_rows_count += len(rows)

        session.flush()

    # remove image_metadata
    rows = session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(clones)).all()
    for row in rows:
        row.lost = 1
    update_rows_count += len(rows)

    session.flush()

    print(f'removed {remove_rows_count} rows, updated {update_rows_count} rows')

    # remove files
    paths = [os.path.join(Env.IMAGES_PATH, im.path) for im in rows]
    for p in paths:
        if not os.path.exists(p):
            continue
        os.remove(p)
        # print(f'removing {p}')

    if auto_commit:
        session.commit()
    else:
        session.flush()

def get_masters(clones:[int], session=None) -> [int]:
    if session is None:
        session = Session

    rows = session.query(ImageDupe).filter(ImageDupe.image1.in_(clones)).all() + \
           session.query(ImageDupe).filter(ImageDupe.image2.in_(clones)).all()

    master = []
    for row in rows:
        if not row.image1 in master:
            master.append(row.image1)
        if not row.image2 in master:
            master.append(row.image2)

    return list(filter(lambda id: not id in clones, master))