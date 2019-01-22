#!/usr/bin/env python3

from Server import Server
from Client import Client
from MediaItem import MediaItem

import signal
from datetime import datetime
import sys


def get_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def signal_handler(signal, frame):
	print('{}: Stopping (Received SIGINT)'.format(get_time()))
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C

	playlist = []
	playlist.append(MediaItem('./videos/Robot Club.webm'))
	playlist.append(MediaItem('./videos/Dog.mkv'))
	playlist.append(MediaItem('./videos/seagull.webm'))
	playlist.append(MediaItem('./videos/cat.wav.mkv'))

	server = Server()
	server = server.start()

	while True:
		for i in playlist:
			client = Client(i,server)
			client.play()

	server.terminate()

	# while True:
	# 	for i in playlist:
	# 		client = Client(i)
	# 		client.play()
	# 		while True:
	# 			bytes_in = client.process.stdout.read(4096)
	# 			if not bytes_in:
	# 				break
	# 			server.process.stdin.write(bytes_in)

	# server.wait()

if __name__ == "__main__": main()



