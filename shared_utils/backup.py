import os
import shutil
from datetime import datetime

from shared_utils.env import Env


def make_database_backup(marker:str='',force:bool=False):
    if not os.path.exists(Env.DB_FILE):
        print(f'No existing database found to backup.')
        return

    db_file = os.path.splitext(Env.DB_NAME)
    db_file_name = f'{db_file[0]}_'
    db_file_ext  = f'{db_file[1]}' if len(db_file) > 1 else ''
    time_fmt = '%Y-%m-%d_%H-%M'
    now = datetime.now() # intentionally without tz=timezone.utc
    backup_interval = 60 * Env.DB_BACKUP_INTERVAL # seconds
    path = Env.DB_BACKUP_PATH

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    backup_files = [f for f in os.listdir(path) if f.startswith(db_file_name) and os.path.isfile(os.path.join(path, f))]
    start_pos = len(db_file_name)
    end_pos = start_pos + len(now.strftime(time_fmt))
    dates = [f[start_pos:end_pos] for f in backup_files]
    dates = sorted([datetime.strptime(d, time_fmt) for d in dates])

    if not force and \
            (len(dates) > 0 and now.timestamp() < (dates[-1].timestamp() + backup_interval)):
        return

    print(f'Backing up database. Found {len(backup_files)} backups, making new one.')

    if marker != '':
        marker = f'_{marker.lower().replace(" ", "_")}'
    backup_name = f'{db_file_name}{now.strftime(time_fmt)}{marker}{db_file_ext}'
    src = Env.DB_FILE
    dst = os.path.join(path, backup_name)
    shutil.copy(src, dst)

    backup_files += [backup_name]
    if len(backup_files) < Env.DB_BACKUP_MAX_COUNT:
        return

    backups = [(os.path.join(path, f), os.path.getctime(os.path.join(path, f))) for f in backup_files]
    backups = sorted(backups, key=lambda b: b[1])
    # print(f'{len(backups)} -> trim {len(backups) - Env.DB_BACKUP_MAX_COUNT}')
    # [print(p) for p in backups[:len(backups) - Env.DB_BACKUP_MAX_COUNT]]
    to_remove = backups[:len(backups) - Env.DB_BACKUP_MAX_COUNT]
    [os.remove(p[0]) for p in to_remove]