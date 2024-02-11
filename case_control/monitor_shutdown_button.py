#! /bin/python

import RPi.GPIO as GPIO
import time
import os


GPIO.setmode(GPIO.BCM)

PIN = 16
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

is_shutting_down = False


while True:
    if GPIO.input(PIN) == 0:
        print('button pressed')

    if GPIO.input(PIN) == 0 and not is_shutting_down:
        is_shutting_down = True
        os.system('sudo systemctl poweroff')

    time.sleep(1)
