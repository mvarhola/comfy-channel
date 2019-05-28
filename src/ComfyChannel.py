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


def signal_handler(signal, frame):
	Logger.LOGGER.log(Logger.TYPE_CRIT,"{} received, exiting program!".format(signal))
	sys.exit(0)

def kill_process(procname):
	for proc in psutil.process_iter():
		# check whether the process name matches
		if proc.name() == procname:
			Logger.LOGGER.log(Logger.TYPE_CRIT,"{} pid:{} killed!".format(proc.name(), proc.pid))
			proc.kill()

def main():
	if len(sys.argv) > 1:
		c.OUTPUT_LOCATION = sys.argv[1]
	
	signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C

	server = Server(c.OUTPUT_LOCATION).start()

	while True:
		scheduler = Scheduler(c.PLAYOUT_FILE)
		for i in scheduler.blocklist:
			for j in i.playlist:
				retries = 0
				client = Client(j,server)
				ret = client.play()

				while ret != 0 and retries < c.MAX_SAME_FILE_RETRIES:
					Logger.LOGGER.log(Logger.TYPE_ERROR,"FFMPEG Return Code {}, trying again".format(ret))
					ret = client.play()
					retries += 1
				
				if retries >= c.MAX_SAME_FILE_RETRIES:
					Logger.LOGGER.log(Logger.TYPE_ERROR,"FFMPEG Return Code {}, giving up!".format(ret))
					Logger.LOGGER.log(Logger.TYPE_CRIT,"{} Retries reached, exiting program!".format(c.MAX_SAME_FILE_RETRIES))
					kill_process("ffmpeg")
					sys.exit(0)

if __name__ == "__main__": main()
