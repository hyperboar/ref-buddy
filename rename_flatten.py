import os

PATH = 'E:\\Distr\\__new\\__new\\Playful Female Poses'

files_mv = []

for root, dir, files in os.walk(PATH):
    for file in files:
        if not file.endswith('jpg') and not file.endswith('mp4') and PATH == root:
            continue
        files_mv.append([os.path.relpath(root, PATH), file])

count = 0
for file in files_mv:
    old = os.path.join(PATH, file[0], file[1])
    new_fname = '_'.join(file[0].replace(' ', '_').split('\\')) + '_' + file[1].replace(' ', '_')
    new = os.path.join(PATH, new_fname)
    os.rename(old, new)
    count += 1

print(f"Renamed {count} files")

