To control the case (status light, power button and fan) of our RPi NAS we need to add a few scripts. See below for details.

---

I've connected the green status LED to pin 26 of the Raspberry Pi. To automatically turn it on when the RPi boots add the following line to file /boot/firmware/config.txt (previously located at /boot/config.txt):

  gpio=26=op,dh

Make sure it's not in the section specific to the compute module 4 indicated with [cm4].

---

To enable the shutdown button copy script monitor_shutdown_button.py to /usr/local/bin and make it executable with `sudo chmod +x monitor_shutdown_button.py`. Open the system crontab with `sudo crontab -e` and add the following line:

  @reboot /usr/local/bin/monitor_shutdown_button.py &

Note, there are dedicated pins for powering down/up the Raspberry Pi but they coincide with the pins used for I2C which we'll use for the temperature sensor (you could do software I2C but I find it easier to just use this script). If you have a RPi 5 then there's already a power button on the board, no need to install one separately.

---

For fan control I'm using a 5V Noctua fan with PWM to regulate fan speed. The RPi can only provide 3.3V over its logic pins so the fan will not run on full speed. If it turns out that it's too slow to effectively cool the NAS then I may add a voltage step-up to enable full speed. Also, from what I've read using the RPi's PWM for fan control is not super reliable but it seems to work for the Noctua fan I'm using (it may not work for your fan -- if not then you could consider just using full or no power). To measure the temperature I use a HTU21D sensor. We need to install a library from adafruit to (easily) communicate with it so we'll have to create a virtual environment and install the required packages.

The temperature sensor typically has four pins, one for power (VCC), one ground (GND), one for I2C clock (SCL) and one for I2C data (SDA).

My Noctua fan also has four pins, one for power (VCC), one ground (GND), one for the PWM signal and one that gives information about the current rotation rate of the fan. The last one can be useful, e.g. to check if the fan works as intended, but we need a PWM input to read it. The RPi can't (reliably) read PWM inputs so I'm not using the fourth input. By default the script uses PWM pin 12 for the fan signal but you can change that in the script.

So to set up fan control:
  - pick a folder where you want to save the script, I'm using /home/nas_user/Documents/noctua_fan_control/
  - save the fan control script in /home/nas_user/Documents/noctua_fan_control/noctua_fan_control.py and make it executable (with chmod as before)
  - create a virtual environment with `python -m venv /home/nas_user/Documents/noctua_fan_control/virtual_env`
  - load the environment with `source /home/nas_user/Documents/noctua_fan_control/virtual_env/bin/activate`
  - install library pigpio with `pip3 install pigpio`
  - start and enable pigpio's service with `sudo systemctl start pigpiod` (same with enable)
  - install the adafruit library with `pip install adafruit-circuitpython-HTU21D`
  - make sure i2c (and spi) is enabled in raspi-config

Now you can test the script by running it directly with `python noctua_fan_control.py`. To automatically start it on boot open your user's crontab with `crontab -e` (no sudo rights needed here) and add the following line:

  @reboot /home/nas_user/Documents/noctua_fan_control/virtual_env/bin/python /home/nas_user/Documents/noctua_fan_control/noctua_fan_control.py &
