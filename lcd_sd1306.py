#!/usr/bin/python3

import argparse
from datetime import datetime
from datetime import timedelta
from time import sleep
from time import time
from time import strftime
from time import gmtime
from typing import ChainMap
from lmsmanager import LMS_SERVER
import socket
import netifaces as ni
import signal
import sys
import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
from resizeimage import resizeimage
import adafruit_ssd1306
import requests

# HELP
description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
if_inter = "Network Interface to use"

# PARSER
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="10.0.1.140:9000", help = server_help)
parser.add_argument("-e","--inet", type=str, default="eth0", help = if_inter)
args = parser.parse_args()

# GET IP FROM INTERFACE
hostnm = socket.gethostname()
ip = ni.ifaddresses(args.inet)[ni.AF_INET][0]['addr']

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()

# TURN OFF DISPLAY in CASE OF CTRL+C
def signal_handler(sig, frame):
    print('Catch a Crtl+C !\n Turning off the LCD\n')
    sleep(1)
    disp.poweroff()
    sleep(1)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

top = -2
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

font = ImageFont.truetype('/usr/share/fonts/truetype/DejaVuSans.ttf', 8)

def getPlayersInfo()->dict:
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    try:
        players = myServer.cls_players_list()
        for player in players:
            #print(player["name"])
            if player["isplaying"] == 1:
                return player, players
    except Exception  as err:
        return None, None

    return None, players

def get_from_loop(source_list, key_to_find)->str:
    """
    iterate the list and return the value when the key_to_find is found

    Parameters:
    source_list (list of dict): each element conatins a key and a value
    key_to_find (str): the key to find in the list

    Returns:
        str: the value found or ""

    """
    ret = ""
    for elt in source_list:
        if key_to_find in elt.keys():
            ret = elt[key_to_find]
            break

    return ret

def cleardisp():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.show()

def screen_lms_info():
    """
    Print some info on the LCD when connection to the LMS

    """
    cleardisp()
    if type(server_status) is not dict:
        draw.text((x, top + 0), "IP : " + ip, font=font, fill=255)
        draw.text((x, top + 8), "LMS not found" + ip, font=font, fill=255)
        draw.text((x, top + 16), "No PlaYer" + ip, font=font, fill=255)
    else:
        #player = myServer.cls_player_current_title_status(player_info['playerid'])
        server = server_status["result"]
        draw.text((x, top + 0), "Display IP : " + ip, font=font, fill=255)
        draw.text((x, top + 8), "LMS Version: " + server["version"], font=font, fill=255)
        draw.text((x, top +16), "LMS IP: " + str(server["ip"]), font=font, fill=255)

        lastscan = server['lastscan']
        lastscanreadable = strftime("  %D %H:%M", gmtime(int(lastscan)))
        draw.text((x, top +32), "Last Scan: " + lastscanreadable, font=font, fill=255)
        draw.text((x, top +48),"Albums : " + str(server["info total albums"]), font=font, fill=255)
        draw.text((x, top +56),"Songs  : " + str(server["info total songs"]), font=font, fill=255)
        disp.image(image)
        disp.show()
        sleep(3)



# STARTING
myServer = LMS_SERVER(args.server)
server_status = myServer.cls_server_status()
server = server_status["result"]
screen_lms_info()

# INIT SOME VARS
last_song = {}
album = ""
song_info = None
sleep_duration = 0.4

# Draw a black filled box to clear the image.

# add a timer to switch display on line 4
timer = 0
print("Press Ctrl-C to quit.")
startpos = width
pos = startpos

while True:
    player_info, players = getPlayersInfo()

    if player_info is not None and type(server_status) is dict:
        player = myServer.cls_player_current_title_status(player_info['playerid'])

        song_index = int(player["playlist_cur_index"])
        song = player["playlist_loop"][song_index]
        if int(song["id"]) != 0:
            #lcd.display_on()
            # When id is positive, it comes from LMS database
            if (song_info is None or song["id"] != song_info["songinfo_loop"][0]["id"]) or int(song["id"]) < 0:
                song_info = myServer.cls_song_info(song["id"], player_info['playerid'])
                if song != last_song:
                    album = get_from_loop(song_info["songinfo_loop"], "album")
                    # if "artist" in song_info["songinfo_loop"][4].keys():
                    artist = get_from_loop(song_info["songinfo_loop"], "artist")
                    if len(artist) == 0:
                        artist = get_from_loop(song_info["songinfo_loop"], "albumartist")
                    song_title = get_from_loop(song_info["songinfo_loop"], "title")
                    if "current_title" in player.keys():
                        current_title = player['current_title']
                    else:
                        current_title = ""
                    samplesize = get_from_loop(song_info["songinfo_loop"], "samplesize")
                    samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                    if samplerate: lesssamplerate = float(samplerate)/1000
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")
                    songtype = get_from_loop(song_info["songinfo_loop"], "type")
                    tracknumber = get_from_loop(song_info["songinfo_loop"], "tracknum")
                    trackyear = get_from_loop(song_info["songinfo_loop"], "year")
                    duration = get_from_loop(song_info["songinfo_loop"],"duration")
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks'])

        if False:
            pass

        else:
            title = song_title
            coverurl = "http://" + str(server["ip"]) + "/music/current/cover.jpg"
            r = requests.get(coverurl)
            with open("/tmp/cover.jpg", "wb") as f:
                f.write(r.content)
            
            # change between image and song info
            lasttimer = int(str(timer)[-1:])
            line = 0
            maxlen = 28
            if (lasttimer < 6):
                cleardisp()
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                # if more than 30 characters go to next line
                if len(artist) > maxlen:
	                draw.text((x, top + 0), "" + artist[0:maxlen], font=font, fill=255)
	                draw.text((x, top + 8), "" + artist[maxlen:], font=font, fill=255)
	                line += 8
                else:
                        draw.text((x, top + 0), " " + artist, font=font, fill=255)

                if len(album) > maxlen:
                        draw.text((x, top + 8 + line), "" + album[0:maxlen], font=font, fill=255)
                        draw.text((x, top + 16 + line), "" + album[maxlen:], font=font, fill=255)
                        line += 8
                else:
                        draw.text((x, top + 8 + line), "" + album, font=font, fill=255)
	                
                title = "Titre: " + title 
                if len(title) > maxlen: 
                    draw.text((x, top + 16 + line), "" + title[0:maxlen], font=font, fill=255)
                    draw.text((x, top + 24 + line), "" + title[maxlen:], font=font, fill=255)
                    line += 8
                else:
                    draw.text((x, top + 16 + line), "" + title, font=font, fill=255)
                    
                if line < 15:
                    if int(trackyear) != 0:
                        draw.text((x, top + 24 + line), "Année :" + str(trackyear), font=font, fill=255)
                        line += 8

                samplerate = str(lesssamplerate)
                # handle case of SACD
                if bitrate == "0":
                    bitrate = ''

                elapsed = strftime("%M:%S", gmtime(player["time"])) + "   (" + strftime("%M:%S", gmtime(int(duration))) + ")"

                draw.text((x, top + 32 + line), "    " + samplesize + " / " + samplerate + "  " + bitrate + "  " + songtype, font=font, fill=255)
                draw.text((x, top + 40 + line), "    " + track_pos + "    " + elapsed, font=font, fill=255)
                disp.image(image)
                disp.show()
            else:
                cleardisp()
                # show the cover in 1 bit format ! very ugly
                img = Image.open('/tmp/cover.jpg')
                img = Image.open('/tmp/cover.jpg').convert('1')
                img = resizeimage.resize_contain(img, [128, 64], resample=Image.LANCZOS, bg_color=(0, 0, 0, 0))
                img.save('/tmp/cover.ppm')
                img = Image.open('/tmp/cover.ppm').convert('1')
                disp.image(img)
                disp.show()

        last_song = song
        timer += 1
        sleep(sleep_duration)
    else:
        cleardisp()
        today = datetime.today()
        draw.text((x, top + 0), "IP : " + ip, font=font, fill=255)
        draw.text((x, top + 8), today.strftime("Date: %d/%m/%Y"), font=font, fill=255)
        draw.text((x, top + 16), today.strftime("Clock: %H:%M:%S"), font=font, fill=255)
        draw.text((x, top + 24), "No LMS Playing Music?", font=font, fill=255)

