#!/usr/bin/python3
"""
# https://github.com/aginies/LMSLCD2020
"""

import argparse
from time import sleep, strftime, gmtime
import signal
import sys
import unicodedata
import netifaces as ni
from lmsmanager import LmsServer
import lcddriver

# HELP
DESCRIPTION = "LMS API Requester"
SERVER_HELP = "ip and port for the server. something like 192.168.1.192:9000"
LCD_HELP = "LCD address something like 0x27"
I2C_HELP = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
IF_INTER = "Network Interface to use"

# PARSER
PARSER = argparse.ArgumentParser(description=DESCRIPTION)
PARSER.add_argument("-s", "--server", type=str, default="10.0.1.144:9000", help=SERVER_HELP)
PARSER.add_argument("-l", "--lcd", type=lambda x: int(x, 0), default=0x27, help=LCD_HELP)
PARSER.add_argument("-i", "--i2cport", type=int, default=1, help=I2C_HELP)
PARSER.add_argument("-e", "--inet", type=str, default="eth0", help=IF_INTER)
ARGS = PARSER.parse_args()

# GET IP FROM INTERFACE
WIP = ni.ifaddresses("wlan0")[ni.AF_INET][0]['addr']

def get_players_info()->dict:
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    try:
        mplayers = MYSERVER.cls_players_list()
        for mplayer in mplayers:
            #print(player["name"])
            if mplayer["isplaying"] == 1:
                return mplayer, mplayers
    except ValueError as err:
        return None, err

    return None, PLAYERS


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
    if not isinstance(SERVER_STATUS, dict):
        LCD.lcd_display_string("IP : " + WIP, 1)
        LCD.lcd_display_string("LMS not found", 2)
        LCD.lcd_display_string("No player!", 3)
    else:
        #player = MYSERVER.cls_player_current_title_status(PLAYER_INFO['playerid'])
        server = SERVER_STATUS["result"]
        LCD.lcd_display_string("IP: wlan0", 1)
        LCD.lcd_display_string(""+WIP, 2)
        LCD.lcd_display_string("LMS Version: " + server["version"], 3)
        #LCD.lcd_display_string("Players counts:" + str(server["player count"]), 4)
        LCD.lcd_display_string("LMS IP: " + str(server["ip"]), 4)
        #LCD.lcd_display_string(PLAYER_INFO["name"], 4)
        sleep(3)
        LCD.lcd_display_string("Last Scan: ", 1)
        lastscan = server['lastscan']
        lastscanreadable = strftime("  %D %H:%M", gmtime(int(lastscan)))
        LCD.lcd_display_string(lastscanreadable, 2)
        LCD.lcd_display_string("Albums : " + str(server["info total albums"]), 3)
        LCD.lcd_display_string("Songs  : " + str(server["info total songs"]), 4)
        sleep(3)


LCD = lcddriver.lcd(address=ARGS.lcd, i2c_port=ARGS.i2cport, columns=20)
# not needed as all lcd write active the screen
#LCD.backlight_on()
#LCD.display_on()

# TURN OFF DISPLAY in CASE OF CTRL+C
def signal_handler(_sig, _frame):
    """
    catch ctr+c
    """
    print('Catch a Crtl+C !\n Turning off the LCD\n')
    LCD.display_off()
    sleep(1)
    LCD.backlight_off()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# workaround to turn off screen
# ecah lcd_write wake up the screen, so we can not do
# display_off backlight_off
# instead display_off and check the backlight_off
# so one is done only, so no more lcd_write
def turnoff():
    """
    turn off display
    """
    LCD.display_off()
    sleep(2)

# STARTING
MYSERVER = LmsServer(ARGS.server)
SERVER_STATUS = MYSERVER.cls_server_status()
screen_lms_info()

# INIT SOME VARS
LAST_SONG = {}
ALBUM = ""
SONG_INFO = None
SLEEP_DURATION = 0.5

# add a timer to switch display on line 4
TIMER = 0
# was here to turn off the screen value
WASHERE = 0
while True:
    PLAYER_INFO, PLAYERS = get_players_info()

    if PLAYER_INFO is not None and isinstance(SERVER_STATUS, dict):
        PLAYER = MYSERVER.cls_player_current_title_status(PLAYER_INFO['playerid'])

        SONG_INDEX = int(PLAYER["playlist_cur_index"])
        SONG = PLAYER["playlist_loop"][SONG_INDEX]
        if int(SONG["id"]) != 0:
            #LCD.display_on()
            # When id is positive, it comes from LMS database
            #if (SONG_INFO is None or SONG["id"] != SONG_INFO["songinfo_loop"][0]["id"]) or int(SONG["id"]) < 0:
            if SONG_INFO is None or int(SONG["id"]) < 0:
                SONG_INFO = MYSERVER.cls_song_info(SONG["id"], PLAYER_INFO['playerid'])
                if SONG != LAST_SONG:
                    ALBUM = get_from_loop(SONG_INFO["songinfo_loop"], "album")
                    # if "ARTIST" in SONG_INFO["songinfo_loop"][4].keys():
                    ARTIST = get_from_loop(SONG_INFO["songinfo_loop"], "artist")
                    if not ARTIST:
                        ARTIST = get_from_loop(SONG_INFO["songinfo_loop"], "albumartist")
                    SONG_TITLE = get_from_loop(SONG_INFO["songinfo_loop"], "title")
                    if "current_title" in PLAYER.keys():
                        CURRENT_TITLE = PLAYER['current_title']
                    else:
                        CURRENT_TITLE = ""
                    SAMPLESIZE = get_from_loop(SONG_INFO["songinfo_loop"], "samplesize")
                    if SAMPLESIZE == "":
                        SAMPLESIZE = "16"
                    SAMPLERATE = get_from_loop(SONG_INFO["songinfo_loop"], "samplerate")
                    if SAMPLERATE:
                        LESSSAMPLERATE = float(SAMPLERATE)/1000
                    BITRATE = get_from_loop(SONG_INFO["songinfo_loop"], "bitrate")
                    SONGTYPE = get_from_loop(SONG_INFO["songinfo_loop"], "type")
                    TRACKNUMBER = get_from_loop(SONG_INFO["songinfo_loop"], "tracknum")
                    TRACKYEAR = get_from_loop(SONG_INFO["songinfo_loop"], "year")
                    if int(TRACKYEAR) == 0:
                        ALBUMYEAR = ALBUM
                    else:
                        ALBUMYEAR = ALBUM + " (" + TRACKYEAR + ")"

                    DURATION = get_from_loop(SONG_INFO["songinfo_loop"], "duration")
                    #dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(DURATION)))
                    TRACK_POS = str(int(PLAYER['playlist_cur_index']) + 1) + "/" + str(PLAYER['playlist_tracks'])
                    DECAL1 = 0
                    DECAL2 = 0
                    DECAL3 = 0

        ARTIST = unicodedata.normalize('NFD', ARTIST).encode('ascii', 'ignore').decode("utf-8")
        ALBUM = unicodedata.normalize('NFD', ALBUM).encode('ascii', 'ignore').decode("utf-8")
        SONG_TITLE = unicodedata.normalize('NFD', SONG_TITLE).encode('ascii', 'ignore').decode("utf-8")
        TITLE = SONG_TITLE

        if SONG != LAST_SONG:
            pass
        else:
            WASHERE = 0
            LCD.display_on()
            MAX_CAR1 = len(ARTIST) - 20
            MAX_CAR2 = len(ALBUMYEAR) - 20
            MAX_CAR3 = len(TITLE) -20
            if DECAL1 > MAX_CAR1:
                DECAL1 = 0
            if DECAL2 > MAX_CAR2:
                DECAL2 = 0
            if DECAL3 > MAX_CAR3:
                DECAL3 = 0

            LCD.lcd_display_string(ARTIST[DECAL1:20 + DECAL1], 1)
            LCD.lcd_display_string(ALBUMYEAR[DECAL2:20 + DECAL2], 2)
            LCD.lcd_display_string(TITLE[DECAL3:20 + DECAL3], 3)

            # change between RATE of the songs and time remaining
            LASTTIMER = int(str(TIMER)[-1:])
            if LASTTIMER < 4:
                SAMPLERATE = str(LESSSAMPLERATE)
                # handle case of SACD
                if BITRATE == "0":
                    BITRATE = ''
                if SAMPLESIZE == "0":
                    SAMPLESIZE = "16"
                LCD.lcd_display_string((SAMPLESIZE + "/" + SAMPLERATE + ' ' + BITRATE)[:20] + " " + SONGTYPE, 4)
            else:
                ELAPSED = strftime("%M:%S", gmtime(PLAYER["time"])) + " (" + strftime("%M:%S", gmtime(int(DURATION))) + ")"
                LCD.lcd_display_string("" + TRACK_POS + " " + ELAPSED, 4)

            DECAL1 = DECAL1 + 1
            DECAL2 = DECAL2 + 1
            DECAL3 = DECAL3 + 1

        LAST_SONG = SONG
        TIMER += 1
        sleep(SLEEP_DURATION)
    else:
        #today = datetime.today()
        #LCD.lcd_display_string("IP : " + ip, 1)
        #LCD.lcd_display_string(today.strftime("Date: %d/%m/%Y"), 2)
        #LCD.lcd_display_string(today.strftime("Clock: %H:%M:%S"), 3)
        # backlight off each time, turn off only if not done previously
        LCD.backlight_off()
        if WASHERE != 1:
            WASHERE = 1
            turnoff()
        else:
            sleep(2)
