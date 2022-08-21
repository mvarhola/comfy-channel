#!/usr/bin/env python3

import signal
import sys
import argparse
import random
import psutil

import Config as c
import Logger
import Generator
from datetime import datetime
from Client import Client
from MediaItem import MediaItem
from Scheduler import Scheduler
from Server import Server

# Define and explain the arguments that can be passed to the program


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="output location (stream url)",
                        action="store")
    parser.add_argument("-ua", "--upnext_audio_file", help="folder for upnext audio files",
                        action="store")
    parser.add_argument("-uv", "--upnext_video_file", help="folder for upnext video files",
                        action="store")
    parser.add_argument("-uw", "--upnext_wisdom_file", help="file for wisdom text",
                        action="store")
    parser.add_argument("-f", "--font_file", help="font file for overlay text",
                        action="store")
    parser.add_argument("-p", "--playout_file", help="playout config file",
                        action="store")
    parser.add_argument("-1", "--once", help="only run through playout once",
                        action="store_true")

    args = vars(parser.parse_args())

    if args['output']:
        c.OUTPUT_LOCATION = args['output']
    if args['upnext_audio_file']:
        c.SCHEDULER_UPNEXT_AUDIO_FOLDER = args['upnext_audio_file']
    if args['upnext_video_file']:
        c.SCHEDULER_UPNEXT_VIDEO_FOLDER = args['upnext_video_file']
    if args['upnext_wisdom_file']:
        c.SCHEDULER_UPNEXT_WISDOM_FILE = args['upnext_wisdom_file']
    if args['font_file']:
        c.CLIENT_DRAWTEXT_FONT_FILE = args['font_file']
        c.SERVER_DRAWTEXT_FONT_FILE = args['font_file']
    if args['playout_file']:
        c.PLAYOUT_FILE = args['playout_file']
    if args['once']:
        c.LOOP = False
    return args

# Exit program if signal received


def signal_handler(signal, frame):
    Logger.LOGGER.log(Logger.TYPE_CRIT,
                      "{} received, exiting program!".format(signal))
    sys.exit(0)

# Kill all processes matching a name


def kill_process(procname):
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == procname:
            Logger.LOGGER.log(
                Logger.TYPE_CRIT, "{} pid:{} killed!".format(proc.name(), proc.pid))
            proc.kill()

# Play an item to the Server


def play_item(item, server):
    retries = 0
    client = Client(item, server)
    while True:
        ret = client.play()
        if ret != 0:
            Logger.LOGGER.log(
                Logger.TYPE_ERROR, "FFMPEG Return Code {}, trying again".format(ret))
            retries += 1
            # (if a file fails to play several times consecutively, shut down)
            if retries >= c.MAX_SAME_FILE_RETRIES:
                Logger.LOGGER.log(
                    Logger.TYPE_ERROR, "Retry limit reached, giving up!")
                return 1
        else : 
            client.stop()
            return 0

# Main program


def main():
    init_args()  # initialize and parse the passed arguments
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C
    server = Server(c.OUTPUT_LOCATION).start()  # Start the server
    consecutive_retries = 0

    # Main loop
    while True:
        c.TIME_INDEX = datetime.now()
        bumplist = Generator.gen_playlist(c.BUMP_FOLDER, num_files=len(listdir(c.BUMP_FOLDER)), mode="shuffle") # Playlist of bumps
        scheduler = Scheduler(c.PLAYOUT_FILE) # Create a schedule using full playout file
        Logger.LOGGER.log(Logger.TYPE_INFO,
            'Scheduler Created, PLAYOUT_FILE: {}'.format(c.PLAYOUT_FILE))
        for block in scheduler.blocklist: 			# Play each block in the schedule
            for x in range(len(block.playlist)):    # Play each file in the block
                ret = play_item(block.playlist[x], server)
                if ret == 0: # If item played successfully, roll bump chance
                    # Only attempt bump chance on regular items, and not the last item
                    if len(bumplist) > 0 and block.playlist[x].media_type == "regular" and x < len(block.playlist) - 1 and random.random() > 1-block.bump_chance:
                        Logger.LOGGER.log(Logger.TYPE_INFO,"Bump chance succeeded, playing bump.")
                        play_item(random.SystemRandom().choice(bumplist), server)
                else: # else, increment consecutive retries
                    consecutive_retries += 1
                    if consecutive_retries >= c.MAX_CONSECUTIVE_RETRIES:
                        Logger.LOGGER.log(Logger.TYPE_CRIT, "{} Retries consecutive reached, shutting down!".format(consecutive_retries))
                        kill_process("ffmpeg")
                        sys.exit(0)
        if not c.LOOP:
            Logger.LOGGER.log(Logger.TYPE_INFO,'Schedule Finished, shutting down.')
            sys.exit(0)
        else: Logger.LOGGER.log(Logger.TYPE_INFO,'Schedule Finished, looping.')
    



if __name__ == "__main__":
    main()
