#!/usr/bin/python3
# for LCD ili9341
# https://github.com/aginies/LMSLCD2020
#

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

# GPIO ili9341
import time
import random
import busio
import digitalio
import board
from PIL import Image, ImageDraw
import urllib3
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.ili9341 as ili9341

# Configuratoin for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D9)
dc_pin = digitalio.DigitalInOut(board.D10)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000
LCDWIDTH = 320
LCDHEIGHT = 240

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create the ILI9341 display:
display = ili9341.ILI9341(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            width=LCDWIDTH,
            height=LCDHEIGHT,
            baudrate=BAUDRATE
            )

font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", 24)

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

def screen_lms_info():
    """
    Print some info on the LCD when connection to the LMS

    """
    if type(server_status) is not dict:
        print("IP: %s", ip)
        print("LMS not found")
        print("No player!")
    else:
        print("LCD Displayer's IP: ", ip)
        print("LMS Version: " + server["version"], 3)
        print("LMS IP: " + str(server["ip"]))
        #lcd.lcd_display_string(player_info["name"], 4)
        sleep(3)
        lastscan = server['lastscan']
        lastscanreadable = strftime("  %D %H:%M", gmtime(int(lastscan)))
        print("Last Scan: " + lastscanreadable)
        print("Albums : " + str(server["info total albums"]))
        print("Songs  : " + str(server["info total songs"]))
        sleep(3)



# TURN OFF DISPLAY in CASE OF CTRL+C
def signal_handler(sig, frame):
    print('Catch a Crtl+C !\n Turning off the LCD\n')
    #lcd.display_off()
    sleep(1)
    #lcd.backlight_off()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# STARTING
myServer = LMS_SERVER(args.server)
server_status = myServer.cls_server_status()
server = server_status["result"]
screen_lms_info()

# INIT SOME VARS
last_song = {}
album = ""
song_info = None
sleep_duration = 1

while True:
    player_info, players = getPlayersInfo()

    if player_info is not None and type(server_status) is dict:
        player = myServer.cls_player_current_title_status(player_info['playerid'])

        song_index = int(player["playlist_cur_index"])
        song = player["playlist_loop"][song_index]
        if int(song["id"]) != 0:
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
                    if samplerate : lesssamplerate = float(samplerate)/1000
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")
                    songtype = get_from_loop(song_info["songinfo_loop"], "type")
                    tracknumber = get_from_loop(song_info["songinfo_loop"], "tracknum")
                    trackyear = get_from_loop(song_info["songinfo_loop"], "year")
                    # dont display year if not know
                    print(trackyear)
                    if trackyear == 0:
                        albumyear = album
                    else:
                        albumyear = album + " (" + trackyear + ")"

                    duration = get_from_loop(song_info["songinfo_loop"],"duration")
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks'])

        if False:
            pass

        else:
            title = song_title
#            print("song_title:" + song_title)
#            print("title: " + title)
#            print("last song: %s",  last_song)
#            print("song: %s",  song)

            # ONLY CHANGE DISPLAY IF THE SONG CHANGE
            if song != last_song:
                #                print("meme chanson, je ne fais rien")
                #                print("pas la meme chanson!")
                coverurl = "http://" + str(server["ip"]) + "/music/current/cover.jpg"
                print(coverurl)
                print(artist)
                print(albumyear)
                print(title)

                # TEST THE SCREEN
                # draw black filled box
                draw.rectangle((0, 0, width, height), outline=0, fill=0)

                for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
                    display.fill(color565(color))
                # Clear the display
                display.fill(0)
                # Draw a red pixel in the center.
                display.pixel(display.width // 2, display.height // 2, color565(255, 0, 0))
                # Pause 2 seconds.
                time.sleep(2)
                # Clear the screen a random color
                display.fill(
                    color565(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                )
                sleep(2)

                # DISPLAY THE COVER
                image = Image.open(urllib2.urlopen(coverurl))
                # Scale the image to the smaller screen dimension
                image_ratio = image.width / image.height
                screen_ratio = width / height
                if screen_ratio < image_ratio:
                    scaled_width = image.width * height // image.height
                    scaled_height = height
                else:
                    scaled_width = width
                    scaled_height = image.height * width // image.width
                image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

                # Crop and center the image
                x = scaled_width // 2 - width // 2
                y = scaled_height // 2 - height // 2
                image = image.crop((x, y, x + width, y + height))
    
                # Display image.
                display.image(image)
                sleep(3) 

                # change between RATE of the songs and time remaining
                samplerate = str(lesssamplerate)
                # handle case of SACD
                if bitrate == "0":
                    bitrate = ''
                print(samplesize + "/" + samplerate + ' ' + bitrate + " " + songtype)
                cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
                CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
                # Write four lines of text.
                y = top
                draw.text((x, y), CPU, font=font, fill="#FFFF00")
                #y += font.getsize(CPU)[1]

            # SAME SONG, JUST UPDATE THE ELAPSED TIME
            else:
                elapsed = strftime("%M:%S", gmtime(player["time"])) + " (" + strftime("%M:%S", gmtime(int(duration))) + ")"
                print("" + track_pos + "   " + elapsed)
    
            last_song = song
            sleep(sleep_duration)
    else:
        today = datetime.today()
