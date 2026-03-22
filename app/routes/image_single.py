import io
import json
import os
from datetime import datetime, timezone
from typing import Callable

from PIL import Image
from quart import request, send_file, abort, render_template, Blueprint, send_from_directory, \
    current_app, jsonify, Request

from app.common.dto_basic import EmptyResponse
from app.common.exceptions import ImageFileNotFoundError, ThumbNotFoundError, AnimationDataNotFoundError, \
    ImageNotFoundError
from app.common.image_dtos import ImageInfoDto, ImageFavDto, ColorWithCoordsDto, ColorIdDto, NextImageDto
from app.services.image_metadata_controller import ImageMetadataController as Ctrl
from shared_utils.env import Env
from app.models import Session
from app.models.models_lump import Color, ImageColor,Tag
from app.services.server_args_helpers import get_arg, Args
from shared_utils.utils import Utils

routes_image = Blueprint('routes_image', __name__)

@routes_image.route('/study-image/<int:image_id>')
async def send_html(image_id):
    return await render_template('tpl_view_image.html', content_id=image_id, content_url=f"/image/{image_id}")

@routes_image.route('/image-info/<int:image_id>')
async def image_info(image_id):
    with Session() as session:
        image = Ctrl.get_or_raise(session, image_id)
        return jsonify(ImageInfoDto.model_validate(image))

@routes_image.route('/anim-info/<int:image_id>')
async def animation_info(image_id):
    with Session() as session:
        im = Ctrl.get_or_raise(session, image_id)
        path = os.path.join(Env.TMP_PATH_GIF, im.filename + '.json')

        if not os.path.exists(path):
            raise AnimationDataNotFoundError(image_id, part='json')

        return jsonify(json.loads(open(path, 'r').read()))

@routes_image.route('/image/<int:image_id>')
async def send_image(image_id):
    with Session() as session:
        im = Ctrl.get_or_raise(session, image_id)
        ext = os.path.splitext(im.filename)[1]
        if not os.path.exists(im.path_abs):
            raise ImageFileNotFoundError(image_id, im.path_abs)
        return await send_file(im.path_abs, mimetype=f'image/{ext}')

@routes_image.route('/thumb/<filename>')
async def send_image_thumb(filename):
    if not os.path.exists(os.path.join(current_app.config['THUMB_STATIC'], filename)):
        raise ThumbNotFoundError(filename)
    return await send_from_directory(current_app.config['THUMB_STATIC'], filename)

@routes_image.route('/video/<int:item_id>')
async def send_video(item_id):
    with Session() as session:
        im = Ctrl.get_or_raise(session, item_id)
        fn = im.path_abs.replace('.mp4.gif', '.mp4')
        return await send_file(fn, mimetype=f'video/mp4')

@routes_image.route('/open-video')
async def open_video():

    if not os.path.exists(Env.VIDEO_PLAYER_PATH):
        print('No video player set up yet.')
        return

    from urllib.parse import unquote
    path = unquote(request.args.get('path', default=''))

    if path == '':
        print('No path given')
        return

    import subprocess
    # subprocess.Popen([Env.VIDEO_PLAYER_PATH, path], cwd=os.getcwd())
    subprocess.call(Utils.select_file_cmd_os_specific(path))

    return jsonify(EmptyResponse())

@routes_image.route('/anim-frames-zip/<int:image_id>')
async def send_anim_frame_zip(image_id):
    with Session() as session:
        im = Ctrl.get_or_raise(session, image_id)
        fn = im.filename
        path = os.path.join(Env.TMP_PATH_GIF, fn + '.zip')
        if not os.path.exists(path):
            raise AnimationDataNotFoundError(image_id, part='zip')
        return await send_file(path, mimetype=f'application/zip')

@routes_image.route('/set-image-fav/<int:image_id>/<int:is_fav>')
async def set_image_fav(image_id, is_fav):
    with Session() as session:
        im = Ctrl.set_image_fav(image_id, is_fav, session=session)
        return jsonify(ImageFavDto.model_validate(im))

@routes_image.route('/set-image-last-viewed/<int:image_id>')
async def set_image_last_viewed(image_id):
    with Session() as session:
        now = datetime.now(tz=timezone.utc)
        Ctrl.set_image_last_viewed(session, image_id, now)
        return jsonify(EmptyResponse())

@routes_image.route('/color/palette/<int:image_id>')
async def get_color_palette(image_id):
    with Session() as session:
        im = Ctrl.get_or_raise(session, image_id)
        out = [{'id': ic.color.id, 'hex': ic.color.hex, 'x': ic.x, 'y': ic.y} for ic in im.colors]
        return jsonify({'id': image_id, 'palette': out})

@routes_image.route('/color-at-coord/<int:image_id>/<int:x_r>/<int:y_r>')
@routes_image.route('/color-at-coord/<int:image_id>/<float:x_r>/<float:y_r>')
async def get_color_at_coord(image_id, x_r, y_r):
    with Session() as session:
        im = Ctrl.get_or_raise(session, image_id)

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

        return jsonify(ColorWithCoordsDto(x=x_r, y=y_r, hex=hex_color))

@routes_image.route('/save-image-color')
async def save_image_color():
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

    with Session() as session:
        color = session.query(Color).filter(Color.hex == hex_color).first()
        if color is None:
            color = Color(hex=hex_color, color_name=f'image {image_id}')
            session.add(color)
            session.flush()

        session.merge(ImageColor(image_id=image_id, color_id=color.id, x=x, y=y))
        session.commit()

        # color = session.query(Color, )
        return jsonify(ColorIdDto.model_validate(color))

@routes_image.route('/color/palette/remove/<int:image_id>/<int:color_id>')
async def remove_image_color(image_id, color_id):
    with Session() as session:
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

        return jsonify(ColorIdDto(id=color_id))

@routes_image.route('/drawing/save', methods=['POST'])
async def drawing_save():
    import base64

    json = await request.get_json()
    image_id = json['image_id']
    data = json['data']

    prefix = image_id + '_'
    next_count = 1
    other = [int(file.split('_')[1].replace('.png', '')) for file in os.listdir(Env.DRAWING_PATH) if file.startswith(prefix)]
    if len(other) > 0:
        next_count = max(other) + 1

    data = data.split(',')[1]
    path = os.path.join(Env.DRAWING_PATH, f'{prefix}{next_count}.png')

    img = Image.open(io.BytesIO(base64.b64decode(data)))
    img.save(path, 'png')

    return jsonify(EmptyResponse())

@routes_image.route('/next-image/<pattern>/<int:image_id>')
async def next_image(pattern, image_id):
    with Session() as session:
        Ctrl.get_or_raise(session, image_id)

        lookup = {}
        lookup['_'] = lambda im_id, s: next_miss(im_id)
        lookup['fwd_id']  = lambda im_id, s : next_seq_image_id(im_id, 1, s)
        lookup['bck_id']  = lambda im_id, s: next_seq_image_id(im_id, -1, s)
        lookup['fwd_rnd'] = lambda im_id, s: next_random_image_id(im_id, request, s)
        lookup['fwd_name'] = lambda im_id, s: next_image_by_name(im_id, 1, request, s)
        lookup['bck_name'] = lambda im_id,s : next_image_by_name(im_id, -1, request, s)

        next_im:Callable[[int, Session], int|None] = lookup[pattern] if pattern in lookup else lookup['_']

        image_id = next_im(image_id, session)
        return jsonify(NextImageDto.model_validate({'id': image_id, 'pattern': pattern}))

def next_miss(image_id:int):
    raise ImageNotFoundError(image_id)

def next_seq_image_id(image_id:int, direction:int, session):
    target_id = image_id + direction
    im = Ctrl.get_or_raise(session, target_id)
    return im.image_id

def next_random_image_id(image_id: int, req: Request, session:Session) -> int:
    im = Ctrl.get_random_by_request(request=req, image_id=image_id, session=session)
    if im is None:
        raise ImageNotFoundError(image_id)
    return im.image_id

def next_image_by_name(image_id: int, step: int,  req: Request, session:Session) -> int:
    im = Ctrl.get_next_name_by_request(image_id=image_id, step=step, request=req, session=session)
    if im is None:
        raise ImageNotFoundError(image_id)
    return im.image_id

def next_image_by_date(image_id: int, step: int,  req: Request) -> int:
    return 1