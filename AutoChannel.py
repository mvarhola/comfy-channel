#!/usr/bin/env python3

from Server import Server
from Client import Client
from MediaItem import MediaItem
from Scheduler import Scheduler

import signal
import sys

def signal_handler(signal, frame):
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C

	server = Server()
	server = server.start()

	while True:
		scheduler = Scheduler()
		for i in scheduler.blocklist:
			for j in i.playlist:
				client = Client(j,server)
				client.play()
				client.stop()

	server.terminate()


if __name__ == "__main__": main()



