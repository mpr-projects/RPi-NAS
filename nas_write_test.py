import os
import time


# number of times the test will be run
n = 6

# this is the data that will be copied to the NAS, it should reside on your
# computer and ideally on a drive with fast read speed, eg on an SSD
src = '/path/to/file/or/folder/to/copy/to/MAS'

# this is the folder where a Samba share of our NAS is mounted
dst = '/path/to/Samba/share/mountpoint'

# comand used to copy the data
cmd = 'cp'  # 'cp' or 'rsync'


for i in range(n):
    os.system(f'sync; time {{ {cmd} -r {src} {dst}; sync; }} ')
    time.sleep(2)
    os.system(f'rm -r {os.path.join(dst, os.path.basename(src))}')

    if i != n-1:
        time.sleep(10)
