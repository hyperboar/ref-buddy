import os, shutil

# Script to append folder name to a file names
print('rename')
path = 'D:\\Video\\Pron\\Behind Moon (Q)\\Behind Moon (Q) Doujinshi Phallic Girls'

dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

for d in dirs:
	new_p = d.replace('[ENG] ', '').replace('[JAP] ', '')
	if d == new_p:
		continue
	os.rename(os.path.join(path, d), os.path.join(path, new_p))

dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

for d in dirs:
	files = [f for f in os.listdir(os.path.join(path, d))]
	# if len(files) > 50:
	# 	continue

	for f in files:
		if f.startswith(d):
			continue
		os.rename(os.path.join(path, d, f), os.path.join(path, f'{d}_{f}'))

	print(f'renamed in {d} {len(files)} files')

for d in dirs:
	files = [f for f in os.listdir(os.path.join(path, d))]
	for f in files:
		shutil.move(os.path.join(path, d, f), os.path.join(path, d, '..', f))