
class Playlist:
	
	def __init__(self, directory, max_files=5):
		print("Reading {max_files} from {directory}")
		self.dir = directory
		self.files = []

	def next(self):
		self.files.pop()
