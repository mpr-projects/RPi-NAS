#! /bin/python
import os
import time
import contextlib


mount_point = '/nas_mounts'
gh_folder = 'gh'

max_age = 604800  # one week in seconds


# There's currently no log to track which files and directories were deleted. I
# may implement that sometime in the future.


def clean_folder(path):
    for f in os.listdir(path):
        cur_path = os.path.join(path, f)

        # recursively clean directories
        if os.path.isdir(cur_path):
            clean_folder(cur_path)

            # remove directory if it's empty
            with contextlib.suppress(OSError):
                os.rmdir(cur_path)

            continue

        # check age of file and delete if applicable
        mod_time = os.path.getmtime(cur_path)
        cur_time = time.time()

        if cur_time - mod_time > max_age:
            os.remove(cur_path)


if __name__ == '__main__':
    for mp in os.listdir(mount_point):
        cur_path = os.path.join(mount_point, mp)

        if not os.path.isdir(cur_path):
            continue

        # check if gh folder exists
        cur_path = os.path.join(cur_path, gh_folder)

        if not os.path.isdir(cur_path):
            continue

        # check if .gh_trash exists
        cur_path = os.path.join(cur_path, '.gh_trash')

        if not os.path.isdir(cur_path):
            continue

        clean_folder(cur_path)
