class Server:
	
	options = ''	

	def __init__(self):
		self.status = "Initialized"
		self.cmd = ''

	def start(self):
		print("Starting Server")

	def stop(self):
		print("Stopping Server")