# Some useful information:
#
# - about pigpio hardware_PWM: http://abyz.me.uk/rpi/pigpio/python.html#hardware_PWM
# - 25kHz doesn't work for me, the fan goes on and off in large intervals, using 250 instead
# - we can't use the fourth connector of the fan (which returns the current rotation rate)
#   because the RPi can't read a PWM input (reliably)
# - the rpi pwm output is between 0 and 3.3V, the fan expects between 0 and 5V so with 
#   3.3V we won't get the full speed, I'll try it with 3.3V and if there isn't enough
#   cooling then I'll step up the pwm voltage
# - the fan draws ~0.21A, the RPi can provide over 1A (at 5V), since there are no
#   other power hungry devices attached we should have enough power available
#   (powering the fan from the usb hub with pwm from the rpi won't work because the
#    vcc and ground voltages will generally by different between the rpi and the hub)

# useful links:
#  - https://noctua.at/pub/media/wysiwyg/Noctua_PWM_specifications_white_paper.pdf
#  - https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

# make sure pigpio daemon is running with `sudo systemctl start pigpiod` (and enable)

# using adafruit library for temperature sensor:
#  - https://pypi.org/project/adafruit-circuitpython-HTU21D/

# make sure to activate virtual environment where adafruit library is installed before
# running this script

# make sure i2c (and spi) is enabled in raspi-config

import time
import board
import pigpio
from adafruit_htu21d import HTU21D

# settings
fan_on_min = 30 # °C, below this temperature the fan will be off
fan_on_max = 40  # °C, at and above this temperature the fan will be at max (3.3V)
update_sec = 1  # number of seconds between subsequent updates

min_dc = 0.45  # below a certain dutycycle the fan doesn't move, at the min temperature we need at least this dc value
temp_buffer = 2  # °C to go below fan_on_min when cooling (so the fan doesn't contantly turn on and off
pwm_pin = 12

# set up temperature sensor
i2c = board.I2C()
sensor = HTU21D(i2c)

# set up raspberry pi for pigpio
PI = pigpio.pi()
freq = 250  # 25k doesn't work, 250 and 2500 works ... ?


def set_fan(dutycycle):
    PI.hardware_PWM(pwm_pin, freq, int(1000000 * dutycycle))


set_fan(0)
dc_prev = 0
is_cooling = False


while True:
    temp = sensor.temperature

    if temp < fan_on_min - (temp_buffer if is_cooling else 0):
        dc = 0
        is_cooling = False

    elif temp > fan_on_max:
        dc = 1
        is_cooling = True

    else:  # scale fan speed linearly with temperature
        dc = min_dc + max(0, (1 - min_dc) * (temp - fan_on_min) / (fan_on_max - fan_on_min))
        is_cooling = True

    print(f'\nTemperature: {temp:.2f}, Dutycycle: {dc:.2f}', dc)

    # only adjust fan speed for significant temperature changes
    if abs(dc - dc_prev) > 0.05:
        set_fan(dc)

    dc_prev = dc
    time.sleep(update_sec)
