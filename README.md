# LCD display for LMS

Show information from the Logitech Media Server.

* lcd_20x4.py : for an LCD 20x4 screen
* lcd_ili9341.py : for an ili9341 screen

# Python modules used

lcd_20x4.py:

* smbus
* netifaces
* socket
* signal
* json
* argparse

lcd_ili93941.py:

* netifaces
* socket
* signal
* json
* argparse
* PIL
* urllib2
* adafruit_rgb_display
* digitalio
* board

# Common Arguments Options 

* **-s --server** ip and port for the server. something like 192.168.1.192:9000
* **-e --inet** Network Interface to use

## Additional for lcd_20x4

* **-l --lcd** LCD address something like 0x27
* **-i --i2cport** i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2

./lcd_20x4.py -s 10.0.1.29:9000 -l 0x27 -i 0 -e eth0

# Original idea

https://github.com/renaudrenaud/LMSLCD2020

# External Source and code

* http://www.gejanssen.com/howto/i2c_display_2004_raspberrypi/index.html
* https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/
* https://readthedocs.org/projects/rplcd/downloads/pdf/latest/
