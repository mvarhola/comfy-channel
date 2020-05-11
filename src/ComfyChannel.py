#!/usr/bin/env python3

import signal
import sys
import argparse

import psutil

import Config as c
import Logger
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

# Main program


def main():
    init_args()  # initialize and parse the passed arguments
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C
    server = Server(c.OUTPUT_LOCATION).start()  # Start the server

    # Main loop
    while True:
        scheduler = Scheduler(c.PLAYOUT_FILE) # Create a schedule using full playout file
        Logger.LOGGER.log(Logger.TYPE_INFO,
            'Scheduler Created, PLAYOUT_FILE: {}'.format(c.PLAYOUT_FILE))
        for i in scheduler.blocklist: 			# Play each block in the schedule
            for j in i.playlist:				# Play each file in the block
                retries = 0
                client = Client(j, server)
                ret = client.play()

                while ret != 0 and retries < c.MAX_SAME_FILE_RETRIES:
                    Logger.LOGGER.log(
                        Logger.TYPE_ERROR, "FFMPEG Return Code {}, trying again".format(ret))
                    ret = client.play()
                    retries += 1

                # (if a file fails to play several times consecutively, shut down)
                if retries >= c.MAX_SAME_FILE_RETRIES:
                    Logger.LOGGER.log(
                        Logger.TYPE_ERROR, "FFMPEG Return Code {}, giving up!".format(ret))
                    Logger.LOGGER.log(Logger.TYPE_CRIT, "{} Retries reached, exiting program!".format(
                        c.MAX_SAME_FILE_RETRIES))
                    kill_process("ffmpeg")
                    sys.exit(0)


if __name__ == "__main__":
    main()
