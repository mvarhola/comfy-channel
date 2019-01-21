#!/usr/bin/env python3

from Server import Server
from Client import Client

def main():
	server = Server()
	server.start()
	server.stop()

if __name__ == "__main__": main()