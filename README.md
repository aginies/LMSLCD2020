# LCD display for LMS

Logitech Media Server to LCD, use API Python 3 and Request
LCD 20x4 show information from the Logitech Media Server

* lcd_20x4.py : for an LCD screen, 20x4
* lcd_ili9341.py : for a ili9341 screen

# Python modules used

lcd_20x4.py:

* smbus
* netifaces
* time
* socket
* signal
* json
* argparse

lcd_ili93941.py:

* netifaces
* time
* socket
* signal
* json
* argparse
* PIL
* urllib2
* adafruit_rgb_display
* digitalio
* board

# Arguments options

* **-s --server** ip and port for the server. something like 192.168.1.192:9000
* **-l --lcd** LCD address something like 0x27
* **-i --i2cport** i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2
* **-e --inet** Network Interface to  use

./lcd.py -s 10.0.1.29:9000 -l 0x27 -i 0 -e eth0

# Original idea

https://github.com/renaudrenaud/LMSLCD2020

# External Source and code

* http://www.gejanssen.com/howto/i2c_display_2004_raspberrypi/index.html
* https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/
* https://readthedocs.org/projects/rplcd/downloads/pdf/latest/
