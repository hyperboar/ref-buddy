import json
import os
import shutil

from win32_setctime import setctime

from Env import Env

TMP_RESTORE_METADATA_NAMES_LOG = 'log_restore_metadata_filenames.log'

GGL_FOLDER_PATH = 'E:\Distr\__new\Google Photos'
# GGL_FOLDER_PATH = 'E:\Distr\__new\GGL_Test'
# GGL_FOLDER_PATH = 'E:\Distr\__new\Google Photos\Awesome dicks'
METADATA_JSON = 'metadata.json'
GGL_NAME_LIMIT = 46

ARCHIVE_DOWNLOAD_TIMESTAMP = 1687726800

def restore_json_names(root_path, tmp_io):

    for dir_path, dir_names, file_names in os.walk(root_path):

        if len(file_names) == 0:
            continue

        if METADATA_JSON in file_names:
            file_names.remove(METADATA_JSON)

        images = [f for f in file_names if not f.endswith('json')]

        broken_names = [n for n in images if n + '.json' not in file_names]

        if len(broken_names) == 0: continue

        count = 0
        max_count = len(broken_names)
        print(f'Restoring cut metafile names in folder {dir_path} ...')
        print(f'{pers(count,max_count)} Restoring cut metafile names ...', end='')
        # over 46 characters
        for n in broken_names:
            count += 1
            print(f'\r{pers(count,max_count)} Restoring cut metafile names {n}...', end='')
            if len(n) < GGL_NAME_LIMIT + 1:
                continue

            meta = n[:GGL_NAME_LIMIT] + '.json'
            if meta not in file_names:
                continue

            oldname = os.path.join(dir_path, meta)
            newname = os.path.join(dir_path, n + '.json')

            try:
                shutil.move(oldname, newname)
            except FileNotFoundError:
                tmp_io.write(f'FNF error for {oldname}\n')

        print(f'\r{pers(count,max_count)} Restoring cut metafile names... Done' + ' '*30)

def restore_create_date(root_path, tmp_io):

    for dir_path, dir_names, file_names in os.walk(root_path):
        if len(file_names) == 0:
            continue

        if METADATA_JSON in file_names:
            file_names.remove(METADATA_JSON)

        images = [f for f in file_names if not f.endswith('json')]
        if len(images) == 0:
            continue

        count = 0
        max_count = len(images)
        print(f'Restoring creation date in folder {dir_path} ...')
        print(f'{pers(count,max_count)} Restoring creation date ...', end='')
        for im in images:
            count += 1
            path = os.path.join(dir_path, im)
            path_json = path + '.json'

            if not os.path.exists(path_json):
                tmp_io.write(f'NO META {path}\n')
                continue

            old_time = os.path.getctime(path)

            # if old_time < ARCHIVE_DOWNLOAD_TIMESTAMP:
            #     continue

            print(f'\r{pers(count, max_count)} Restoring creation date {path}...', end='')
            with open(path_json, encoding='UTF-8') as json_file:
                data = json.load(json_file)
                cr_time = int(data['photoTakenTime']['timestamp'])

            os.utime(path, (cr_time, cr_time))
            setctime(path, cr_time)

        print(f'\r{pers(count, max_count)} Restoring creation date ... Done' + ' ' * 30)

def pers(cur, max_count):
    return str(int(cur/max_count*100)) + '%'


if __name__ == '__main__':
    tmp_file = os.path.join(Env.TMP_PATH, TMP_RESTORE_METADATA_NAMES_LOG)

    # # restore json names
    # with open(tmp_file, 'a', encoding='UTF-8') as tmp_log:
    #     restore_json_names(GGL_FOLDER_PATH, tmp_log)

    # # restore create date
    with open(tmp_file, 'a', encoding='UTF-8') as tmp_log:
        restore_create_date(GGL_FOLDER_PATH, tmp_log)