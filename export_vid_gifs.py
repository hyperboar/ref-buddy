import math
import os
import subprocess
from datetime import datetime, timedelta
from utils import Utils

class ExportVidGifs:
    """
    Take mp4 file and generate tiny preview (max height 200px) with file extension ".mp4.gif".
    It then can be imported as a general gif.
    Atm preview is first 10 sec of the video, sped up.
    """

    @staticmethod
    def export(folder_path, force=False):
        """
        Using couple shell calls to get video duration and actually convert video to gif.
        """

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

                # getting video's duration in format "0:00:00.0000" by executing shell command and grabbing raw output
                dur_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -sexagesimal "{input_file}"'
                dur_out = subprocess.run(dur_cmd, capture_output=True).stdout.decode("utf-8")

                # convert raw output to total_seconds
                t = datetime.strptime(dur_out, '%H:%M:%S.%f\r\n')
                total_dur = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond).total_seconds()

                # short videos should generate short gif, long videos should be sped up so everything is shown under max_dur seconds
                max_dur = 10.
                min_dur = 4.
                if total_dur < min_dur or math.isclose(total_dur, min_dur):
                    rate = min_dur / total_dur
                    total_dur = min_dur
                elif total_dur < max_dur:
                    rate = 1.
                else:
                    rate = max_dur/ total_dur

                fps = 1.
                dur = min(max_dur, total_dur)

                command = ['ffmpeg',
                           '-hide_banner',
                           '-loglevel', 'quiet',
                           # '-stats',
                           '-y',
                           '-i', input_file,
                           '-t', str(dur),
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

if __name__ == '__main__':
    from Env import Env
    # ExportVidGifs.export(Env.IMAGES_PATH)
    ExportVidGifs.export('E:\\Distr\\__new\\test')