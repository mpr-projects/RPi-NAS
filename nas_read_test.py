import os
import time


# number of times the test will be run
n = 6

# path to a file or folder on a mounted Samba share
src = '/path/to/source/file/or/folder/on/NAS'

# this is where the data will be copied to, ideally it's located on fast
# storage, e.g. an SSD, so the write speed of your computer doesn't influence
# the speed test
dst = '/path/to/some/folder/on/your/computer/'

# comand used to copy the data
cmd = 'rsync'  # 'cp' or 'rsync'


for _ in range(n):
    os.system(f'sync; time {{ {cmd} -r {src} {dst}; sync; }} ')
    time.sleep(2)
    os.system(f'rm -r {os.path.join(dst, os.path.basename(src))}')

    if i != n-1:
        time.sleep(10)
