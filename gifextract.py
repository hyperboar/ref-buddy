import io
import json
import os
from zipfile import ZipFile

import webp
from PIL import Image


'''
Source: https://gist.github.com/BigglesZX/4016539
I searched high and low for solutions to the "extract animated GIF frames in Python"
problem, and after much trial and error came up with the following solution based
on several partial examples around the web (mostly Stack Overflow).

There are two pitfalls that aren't often mentioned when dealing with animated GIFs -
firstly that some files feature per-frame local palettes while some have one global
palette for all frames, and secondly that some GIFs replace the entire image with
each new frame ('full' mode in the code below), and some only update a specific
region ('partial').

This code deals with both those cases by examining the palette and redraw
instructions of each frame. In the latter case this requires a preliminary (usually
partial) iteration of the frames before processing, since the redraw mode needs to
be consistently applied across all frames. I found a couple of examples of
partial-mode GIFs containing the occasional full-frame redraw, which would result
in bad renders of those frames if the mode assessment was only done on a
single-frame basis.

Nov 2012
'''

def process_animation(path, save_path = None, meta=None):
    if path.endswith('.gif'):
        frames = extract_frames_gif(path)
    elif path.endswith('.webp'):
        frames = extract_frames_webp(path)

    info = { 'dur': 0, 'source':path, 'frames': [] }

    if save_path is None:
        save_path = os.path.dirname(path)

    filename = os.path.basename(path)

    # i = 0
    # new_frame = Image.new('RGB', frames[0][0].size)
    # for frame, duration in frames:
    #     new_filename = f"{filename}_{i:03}.jpg"
    #     new_path = os.path.join(save_path, new_filename)
    #
    #     new_frame.paste(frame, (0, 0), frame.convert('RGBA'))
    #     new_frame.save(new_path)
    #
    #     info['frames'].append({'fn': new_path, 'dur': duration})
    #     info['dur'] += duration
    #     i += 1

    obj_frames = []
    for i, (frame, dur) in enumerate(frames):
        file_object = io.BytesIO()
        frame.save(file_object, 'JPEG')
        frame.close()
        obj_frames.append((file_object, dur))

    with ZipFile(os.path.join(save_path, filename + '.zip'), 'w') as zip_file:

        # new_frame = Image.new('RGB', frames[0][0].size)
        for i, (frame, duration) in enumerate(obj_frames):
            new_filename = f'{i:03}.jpg'
            zip_file.writestr(new_filename, frame.getvalue())

            # new_frame.paste(frame, (0, 0), frame.convert('RGBA'))
            # new_frame.save(new_path)

            info['frames'].append({'fn': new_filename, 'dur': duration})
            info['dur'] += duration

        # print(zip_file.infolist())

    if meta is not None:
        for key in meta:
            info[key] = meta[key]

    info_path = os.path.join(save_path, f'{filename}.json')
    if os.path.exists(info_path):
        os.remove(info_path)
    with open(info_path, 'w') as f:
        f.write(json.dumps(info, indent=4))



def analyse_gif(path):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    '''
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results

def extract_frames_gif(path):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyse_gif(path)['mode']

    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    frames = []

    try:
        while True:
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette() and im.mode in ("L", "LA", "P", "PA"):
                im.putpalette(p)

            new_frame = Image.new('RGB', im.size)

            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))
            frames.append((new_frame, im.info['duration']))

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return frames

def extract_frames_webp(path):
    frames = []
    with open(path, 'rb') as f:
        webp_data = webp.WebPData.from_buffer(f.read())

        # get width and height
        dec_config = webp.WebPDecoderConfig.new()
        dec_config.read_features(webp_data)

        # get pixels and timestamps of each frame
        i = 0
        dec = webp.WebPAnimDecoder.new(webp_data)
        for arr, timestamp_ms in dec.frames():
            # `arr` contains decoded pixels for the frame
            # `timestamp_ms` contains the _end_ time of the frame
            tmp_frame = Image.new('RGBA', (dec_config.input.width, dec_config.input.height))
            tmp_frame.frombytes(arr)
            tmp_frame.convert('RGB')
            frame = Image.new('RGB', (dec_config.input.width, dec_config.input.height))
            frame.paste(tmp_frame, (0, 0), tmp_frame.convert('RGBA'))
            frames.append((frame, timestamp_ms))
            i += 1

    # convert absolute timestamps to relative frame durations
    if len(frames) > 1:
        t = frames[0][1]
        for i in range(1, len(frames)):
            frames[i] = (frames[i][0], frames[i][1] - t)
            t += frames[i][1]

    return frames


def main():
    # process_animation('C:\\Users\\might\\Desktop\\2\\Limbus-Company-Lobotomy-Corporation--hettangeway-8004589.gif')
    # process_animation('C:\\Users\\might\\Desktop\\2\\21856079.webp')
    process_animation('C:\\Users\\might\\Desktop\\2\\29741116.webp')


if __name__ == "__main__":
    main()