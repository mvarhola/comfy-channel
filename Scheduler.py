import configparser
import Generator

class Block:

	def __init__(self, name, folder, num_files, bump_chance):
		self.name = name
		self.folder = folder
		self.num_files = num_files
		self.bump_chance = bump_chance
		self.playlist = []

		playlist = Generator.gen_playlist(folder, num_files = int(num_files))
		upnext = Generator.gen_upnext('./upnext/video','./upnext/audio',
											 	playlist = playlist, 
											 	info_file='./upnext/wisdom.txt')
		

		self.playlist += [upnext] + playlist
		
class Scheduler:
	
	def __init__(self, input_file = 'config.ini'):
		self.config = configparser.ConfigParser()
		self.config.read(input_file)

		self.blocklist = []
		
		c = self.config
		for i in self.config.sections():
			block = Block(c[i]['name'], c[i]['folder'], c[i]['files'], c[i]['bump_chance'])
			self.blocklist.append(block)