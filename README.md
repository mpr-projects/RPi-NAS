# RPi-NAS
This repository contains a few scripts that are used in the Raspberry Pi NAS.

Scripts:
- *__nas_smart_test.py__* is a script intended to be run with cron. It starts a S.M.A.R.T. check of a drive, keeps the drive awake and finally writes the output to one or multiple files. See https://www.mpr-projects/... for details.
- *__clean_nas_trash.py__* is a script intended to be run with cron. It deletes all files from Greyhole's trash that are older than a certain amount of time (which can be set in the script). See https://www.mpr-projects/... for details.
