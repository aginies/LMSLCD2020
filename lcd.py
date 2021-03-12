#!/usr/bin/python3
# 
# original code from https://github.com/renaudrenaud/LMSLCD2020
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

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x27"
i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
if_inter = "Network Interface to use"

parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="10.0.1.140:9000", help = server_help)
parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x27, help = lcd_help)
parser.add_argument("-i","--i2cport", type=int, default=1, help = i2c_help)
parser.add_argument("-e","--inet", type=str, default="eth0", help = if_inter)

args = parser.parse_args()
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
        lcd.lcd_display_string("IP : " + ip, 1)
        lcd.lcd_display_string("LMS not found", 2)
        lcd.lcd_display_string("No player!",3)
    else:
        server = server_status["result"]
        lcd.lcd_display_string("IP : " + ip, 1)
        lcd.lcd_display_string("LMS : " + server["version"],2)
        lcd.lcd_display_string("Players counts:" + str(server["player count"]),3)


import lcddriver
lcd = lcddriver.lcd(address = args.lcd, i2c_port = args.i2cport, columns=20)
lcd.display_on()
myServer = LMS_SERVER(args.server)
server_status = myServer.cls_server_status()
screen_lms_info()
sleep(1)

last_song = {}
album = ""
decal = 0
song_info = None
sleep_duration = 0.6

while True:
    # seconds = time()
    today = datetime.today()
    if today.second == 0:
        server_status = myServer.cls_server_status()
    player_info, players = getPlayersInfo()


    if player_info is not None and type(server_status) is dict:
        # sec = int(today.strftime("%S"))
        player = myServer.cls_player_current_title_status(player_info['playerid'])

        song_index = int(player["playlist_cur_index"])
        song = player["playlist_loop"][song_index]

        if int(song["id"]) != 0:
            lcd.display_on()
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
                    lesssamplerate = float(samplerate)/1000
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")

                    duration = get_from_loop(song_info["songinfo_loop"],"duration")
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks'])
                    decal = 0
                    decal1 = 0
                    decal2 = 0
                    decal3 = 0

        if False:
            pass

        elif player["time"] < 2:
            elapsed = strftime("%M:%S", gmtime(player["time"])) + "-" + strftime("%M:%S", gmtime(int(duration)))
            lcd.lcd_display_string("" + track_pos + " " + elapsed, 4)

        else:
#            lcd.display_on()
            title = song_title
            max_car1 = len(artist) - 20
            max_car2 = len(album) - 20
            max_car3 = len(title) -20
            if decal1 > max_car1:
                decal1 = 0
            if decal2 > max_car2:
                decal2 = 0
            if decal3 > max_car3:
                decal3 =0

            lcd.lcd_display_string(artist[decal1:20 + decal1], 1)
            lcd.lcd_display_string(album[decal2:20 + decal2], 2)
            lcd.lcd_display_string(title[decal3:20 + decal3], 3)

            samplerate = str(lesssamplerate)
            # handle case of SACD
            if bitrate == "0":
                bitrate = ''
            lcd.lcd_display_string((samplesize + "/" + samplerate + ' ' + bitrate)[:20], 4)

            decal1 = decal1 + 1
            decal2 = decal2 + 1
            decal3 = decal3 + 1

        last_song = song
        sleep(sleep_duration)
    else:
        today = datetime.today()
        lcd.lcd_display_string("IP : " + ip, 1)
        lcd.lcd_display_string(today.strftime("Date: %d/%m/%Y"), 2)
        #lcd.lcd_display_string(today.strftime("Clock: %H:%M:%S"), 3)
        lcd.lcd_display_string("No LMS Playing Music? ", 4)
        #lcd.backlight_off()
        sleep(1)
