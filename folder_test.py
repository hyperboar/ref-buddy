import os, time

filename = 'C:\\Users\\might\\Desktop\\3'

print(os.path.getsize(filename))
print(time.ctime(os.path.getmtime(filename)))
print(time.ctime(os.path.getctime(filename)))