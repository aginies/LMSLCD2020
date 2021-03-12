# LCD display for LMS

Logitech Media Server to LCD, use API Python 3 and Request
LCD 20x4 show information from the Logitech Media Server

# Python modules used

* smbus
* netifaces
* time
* socket
* json
* argparse

# Arguments options

**-s --server** ip and port for the server. something like 192.168.1.192:9000
**-l --lcd** LCD address something like 0x27
**-i --i2cport** i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2
**-e --inet** Network Interface to  use

# Original idea

https://github.com/renaudrenaud/LMSLCD2020
