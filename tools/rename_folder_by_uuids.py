import sys
import uuid
import os

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} path_to_folder')
        return

    path = sys.argv[1]
    if not os.path.isdir(path):
        print(f'Usage: {sys.argv[0]} path_to_folder')
        print(f'Path {path} is not a folder')
        return

    i = 0
    for file in os.listdir(path):
        if os.path.isdir(file):
            continue

        new_name = str(uuid.uuid4()) + '.' + file.split('.')[-1]
        os.rename(os.path.join(path, file), os.path.join(path, new_name))
        print(f'{file} -> {new_name}')
        i += 1

    print(f'Done. Renamed {i} files.')

if __name__ == '__main__':
    main()
