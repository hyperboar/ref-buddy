import os
from datetime import datetime
from typing import Callable

from PIL import Image
from flask import render_template_string, request, send_file, abort, render_template, Blueprint, send_from_directory, \
    current_app, jsonify, Request, Response

from image_metadata_controller import ImageMetadataController as Ctrl
from Env import Env
from models.models_lump import Session, ImageMetadata, Color, ImageColor, TagSet, Tag
from server_args_helpers import get_arg, Args

routes_image = Blueprint('routes_image', __name__)

@routes_image.route('/image/<int:image_id>')
def send_static_image(image_id):
    session = Session()
    metadata = Ctrl.get_by_id(image_id, session=session)
    ext = os.path.splitext(metadata.filename)[1]
    out = send_file(metadata.path_abs, mimetype=f'image/{ext}')
    session.close()
    return out

@routes_image.route('/thumb/<path>')
def send_static_image_thumb(path):
    return send_from_directory(current_app.config['THUMB_STATIC'], path)

@routes_image.route('/set-image-fav/<int:image_id>/<int:is_fav>')
def set_image_fav(image_id, is_fav):
    r = Ctrl.set_image_fav(image_id, is_fav)
    if not r:
        abort(404, 'Something went wrong, fav not set, probably...')
    return render_template_string('yep')

@routes_image.route('/set-image-last-viewed/<int:image_id>')
def set_image_last_viewed(image_id):
    now = datetime.now()

    r = Ctrl.set_image_last_viewed(image_id, now)

    if not r:
        abort(404, 'Something went wrong, last viewed not updated, probably...')
    return render_template_string('yep')

@routes_image.route('/color/palette/<int:image_id>')
def get_color_palette(image_id):
    session = Session()
    im = session.get(ImageMetadata, image_id)
    out = [{'id': ic.color.id, 'hex': ic.color.hex, 'x': ic.x, 'y': ic.y} for ic in im.colors]
    session.close()
    return jsonify({'id': image_id, 'palette': out})

@routes_image.route('/color-at-coord')
def get_color_at_coord():
    image_id = get_arg(request.args, Args.image_id)
    x_r = float(request.args.get('x'))
    y_r = float(request.args.get('y'))

    session = Session()
    im = session.get(ImageMetadata, image_id)

    hex_color = '#000000'
    with Image.open(im.path_abs) as image:
        width, height = image.size
        x = int(x_r * width)
        y = int(y_r * height)

        # Calculate the average color of the surrounding pixels
        surrounding_pixels = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                pixel = image.getpixel((i, j))
                surrounding_pixels.append(pixel)
        avg_color = tuple(int(sum(channel) / len(channel)) for channel in zip(*surrounding_pixels))

        avg_color = avg_color[:3]
        # Convert the average color to hex
        hex_color = '#%02x%02x%02x' % avg_color

    return jsonify({'hex': hex_color})

@routes_image.route('/save-image-color')
def save_image_color():
    try:
        image_id = get_arg(request.args, Args.image_id)
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
        hex_color = '#' + request.args.get('hex')
        if hex_color == '#':
            raise ValueError
    except ValueError:
        abort(404, 'Some arguments are missing...')
        return

    print(f'{image_id} {x} {y} {hex_color}')
    session = Session()

    color = session.query(Color).filter(Color.hex == hex_color).first()
    if color is None:
        color = Color(hex=hex_color, color_name=f'image {image_id}')
        session.add(color)
        session.flush()

    session.merge(ImageColor(image_id=image_id, color_id=color.id, x=x, y=y))
    session.commit()

    # color = session.query(Color, )
    return jsonify({'id': color.id})

@routes_image.route('/color/palette/remove/<int:image_id>/<int:color_id>')
def remove_image_color(image_id, color_id):
    session = Session()

    im_color_usage = session.query(ImageColor).filter(ImageColor.color_id == color_id).all()
    tag_color_usage = session.query(Tag).filter(Tag.color_id == color_id).count()
    im_count = len(im_color_usage)
    count = im_count + tag_color_usage

    if count == 0:
        return jsonify({})

    if tag_color_usage == 0 or im_count == 1: # not used in tags, used in one image
        session.delete(session.get(Color, color_id))

    session.delete(session.get(ImageColor, (image_id, color_id)))

    session.commit()

    return jsonify({'color_id': color_id})


@routes_image.route('/study-video/<int:item_id>')
def study_video(item_id):
    session = Session()
    metadata = session.get(ImageMetadata, item_id)

    if metadata is None:
        abort(404, f'Error: No video found with id "{item_id}"')

    tag_sets = session.query(TagSet).order_by(TagSet.set_name).all()
    extra = metadata.extras[0].data

    out = render_template('tpl_video.html', image=metadata, extra=extra, tag_sets=tag_sets, tags=[t.tag for t in metadata.tags])
    session.close()
    return out

@routes_image.route('/video/<int:item_id>')
def send_video(item_id):
    session = Session()
    metadata = session.get(ImageMetadata, item_id)

    fn = metadata.path_abs.replace('.mp4.gif', '.mp4')

    out = send_file(fn, mimetype=f'video/mp4')
    session.close()
    return out

@routes_image.route('/open-video')
def open_video():

    if not os.path.exists(Env.VIDEO_PLAYER_PATH):
        print('No video player set up yet.')
        return

    from urllib.parse import unquote
    path = unquote(request.args.get('path', default=''))

    if path == '':
        print('No path given')
        return

    import subprocess
    subprocess.Popen([Env.VIDEO_PLAYER_PATH, path], cwd=os.getcwd())

    return 'ok'


@routes_image.route('/study-image/<int:image_id>')
def study_image(image_id):
    return render_template('tpl_view_image.html', content_id=image_id, content_url=f"/image/{image_id}")


@routes_image.route('/image-info/<int:image_id>')
def image_info(image_id):
    session = Session()
    image = session.get(ImageMetadata, image_id)
    extra = image.extras[0].data if len(image.extras) > 0 else "{}"
    is_video = 1 if image.source_type_id == 2 or image.source_type_id == 3 else 0
    out = render_template('json/tpl_image_info.json.html', image=image, extra=extra, is_video=is_video)
    session.close()

    return Response(response=out, status=200, mimetype="application/json")

@routes_image.route('/next-image/<pattern>/<int:image_id>')
def next_image(pattern, image_id):
    lookup = {}
    lookup['_'] = lambda im_id: None
    lookup['fwd_id']  = lambda im_id: im_id + 1
    lookup['bck_id']  = lambda im_id: im_id - 1
    lookup['fwd_rnd'] = lambda im_id: next_random_image_id(im_id, request)
    lookup['fwd_name'] = lambda im_id: next_image_by_name(im_id, 1, request)
    lookup['bck_name'] = lambda im_id: next_image_by_name(im_id, -1, request)

    next_im: Callable[[int], int | None] = lookup[pattern] if pattern in lookup else lookup['_']

    image_id = next_im(image_id)
    return jsonify({'id': image_id, 'pattern': pattern}) if image_id else abort(404)

def next_random_image_id(image_id: int, req: Request) -> int:
    session = Session()
    metadata = Ctrl.get_random_by_request(request=req, image_id=image_id, session=session)
    if metadata is None:
        raise Exception(f'No images found (id:{image_id})')
    session.close()
    return metadata.image_id

def next_image_by_name(image_id: int, step: int,  req: Request) -> int:
    session = Session()
    metadata = Ctrl.get_next_name_by_request(image_id=image_id, step=step, request=req, session=session)
    if metadata is None:
        raise Exception(f'No images found (id:{image_id})')
    session.close()
    return metadata.image_id

def next_image_by_date(image_id: int, step: int,  req: Request) -> int:
    return 1
