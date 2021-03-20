#!/usr/bin/python3
# 
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
from lmsmanager import LmsServer
import socket
import netifaces as ni
import signal
import sys

# HELP
description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x27"
i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
if_inter = "Network Interface to use"

# PARSER
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="10.0.1.140:9000", help = server_help)
parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x27, help = lcd_help)
parser.add_argument("-i","--i2cport", type=int, default=1, help = i2c_help)
parser.add_argument("-e","--inet", type=str, default="eth0", help = if_inter)
args = parser.parse_args()

# GET IP FROM INTERFACE
hostnm = socket.gethostname()
wip = ni.ifaddresses("wlan0")[ni.AF_INET][0]['addr']

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
        lcd.lcd_display_string("IP : " + ip, 1)
        lcd.lcd_display_string("LMS not found", 2)
        lcd.lcd_display_string("No player!",3)
    else:
        #player = myServer.cls_player_current_title_status(player_info['playerid'])
        server = server_status["result"]
        lcd.lcd_display_string("IP: wlan0", 1)
        lcd.lcd_display_string("" + wip, 2)
        lcd.lcd_display_string("LMS Version: " + server["version"], 3)
        #lcd.lcd_display_string("Players counts:" + str(server["player count"]), 4)
        lcd.lcd_display_string("LMS IP: " + str(server["ip"]), 4)
        #lcd.lcd_display_string(player_info["name"], 4)
        sleep(3)
        lcd.lcd_display_string("Last Scan: ", 1)
        lastscan = server['lastscan']
        lastscanreadable = strftime("  %D %H:%M", gmtime(int(lastscan)))
        lcd.lcd_display_string(lastscanreadable, 2) 
        lcd.lcd_display_string("Albums : " + str(server["info total albums"]), 3)
        lcd.lcd_display_string("Songs  : " + str(server["info total songs"]), 4)
        sleep(3)


import lcddriver
lcd = lcddriver.lcd(address = args.lcd, i2c_port = args.i2cport, columns=20)
# not needed as all lcd write active the screen
#lcd.backlight_on()
#lcd.display_on()

# TURN OFF DISPLAY in CASE OF CTRL+C
def signal_handler(sig, frame):
    print('Catch a Crtl+C !\n Turning off the LCD\n')
    lcd.display_off()
    sleep(1)
    lcd.backlight_off()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# workaround to turn off screen 
# ecah lcd_write wake up the screen, so we can not do
# display_off backlight_off 
# instead display_off and check the backlight_off
# so one is done only, so no more lcd_write
def turnoff():
    lcd.display_off()
    sleep(2)

# STARTING
myServer = LmsServer(args.server)
server_status = myServer.cls_server_status()
screen_lms_info()

# INIT SOME VARS
last_song = {}
album = ""
song_info = None
sleep_duration = 0.8

# add a timer to switch display on line 4
timer = 0
# was here to turn off the screen value
washere = 0
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
                    print("D: ", samplesize)
                    samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                    if samplerate: lesssamplerate = float(samplerate)/1000
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")
                    songtype = get_from_loop(song_info["songinfo_loop"], "type")
                    tracknumber = get_from_loop(song_info["songinfo_loop"], "tracknum")
                    trackyear = get_from_loop(song_info["songinfo_loop"], "year")
                    if int(trackyear) == 0:
                        albumyear = album
                    else:
                        albumyear = album + " (" + trackyear + ")"

                    duration = get_from_loop(song_info["songinfo_loop"],"duration")
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks'])
                    decal1 = 0
                    decal2 = 0
                    decal3 = 0

        if False:
            pass

        else:
            title = song_title
            if song != last_song:
                pass
            else:
                washere = 0
                lcd.display_on()
                max_car1 = len(artist) - 20
                max_car2 = len(albumyear) - 20
                max_car3 = len(title) -20
                if decal1 > max_car1:
                    decal1 = 0
                if decal2 > max_car2:
                    decal2 = 0
                if decal3 > max_car3:
                    decal3 =0

                lcd.lcd_display_string(artist[decal1:20 + decal1], 1)
                lcd.lcd_display_string(albumyear[decal2:20 + decal2], 2)
                lcd.lcd_display_string(title[decal3:20 + decal3], 3)
    
                # change between RATE of the songs and time remaining
                lasttimer = int(str(timer)[-1:])
                if (lasttimer < 4):
                    samplerate = str(lesssamplerate)
                    # handle case of SACD
                    if bitrate == "0":
                        bitrate = ''
                    if samplesize == "0":
                        samplesize = "16"
                    lcd.lcd_display_string((samplesize + "/" + samplerate + ' ' + bitrate)[:20] + " " + songtype, 4)
                else:
                    elapsed = strftime("%M:%S", gmtime(player["time"])) + " (" + strftime("%M:%S", gmtime(int(duration))) + ")"
                    lcd.lcd_display_string("" + track_pos + " " + elapsed, 4)
    
                decal1 = decal1 + 1
                decal2 = decal2 + 1
                decal3 = decal3 + 1
    
            last_song = song
            timer += 1
            sleep(sleep_duration)
    else:
        #today = datetime.today()
        #lcd.lcd_display_string("IP : " + ip, 1)
        #lcd.lcd_display_string(today.strftime("Date: %d/%m/%Y"), 2)
        #lcd.lcd_display_string(today.strftime("Clock: %H:%M:%S"), 3)
        # backlight off each time, turn off only if not done previously
        lcd.backlight_off()
        if washere != 1:
            washere = 1
            turnoff()
        else:
            sleep(2)
            pass
