import os
import subprocess
from utils import Utils

class ExportVidGifs:
    """
    Take mp4 file and generate tiny preview (max height 200px) with file extension ".mp4.gif".
    It then can be imported as a general gif.
    Atm preview is first 10 sec of the video, sped up.
    """

    @staticmethod
    def export(folder_path, force=False):

        if not Utils.is_windows():
            print("Preview generation for videos works only for windows at the moment :(")
            return

        video_ext = '.mp4'
        out_ext = '.gif'

        vids = []
        print('Searching for videos to generate gif preview...', end='')
        for dir_path, dir_names, filenames in os.walk(folder_path):
            # print(filenames)
            vids += [(fn, dir_path) for fn in filenames if fn.endswith(video_ext) and not os.path.exists((os.path.join(dir_path, fn) + out_ext))]

            # [print(os.path.join(dir_path, v)) for v in vids]

        if len(vids) == 0:
            print('')
        else:
            print(f'\rSearching for videos to generate gif preview... Found {len(vids)} videos to process')

            i = 1
            max_i = len(vids)
            for filename, dir_path in vids:
                input_file = os.path.join(dir_path, filename)
                output_file = input_file + out_ext

                if not force and os.path.exists(output_file):
                    continue

                print(f'  ({i}/{max_i}) Processing "{input_file}"...', end='')

                # fps = 0.8#1./5
                # rate = 1./5

                time = 10
                rate = 1. / 5
                fps = 1 - rate
                command = ['ffmpeg',
                           '-hide_banner',
                           '-loglevel', 'quiet',
                           # '-stats',
                           '-y',
                           '-i', input_file,
                           '-t', str(time),
                           '-vf',
                           f'setpts={str(rate)}*PTS,scale=-1:200:flags=lanczos,fps={str(fps)},split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
                           '-loop', '0',
                           output_file]
                # print(command)

                subprocess.call(command)

                # timestamp sync
                Utils.sync_file_timestamps(input_file, output_file)

                print(f'\r  ({i}/{max_i}) Processing "{input_file}"... Done' + ' ' * 40)

                i += 1

        print('Searching for videos to generate gif preview... Done')