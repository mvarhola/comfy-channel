import ffmpeg
import subprocess
from datetime import datetime

devnull = subprocess.DEVNULL

def get_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Client:

	def __init__(self, media_item, server):
		self.ff = ''
		self.cmd = ''
		self.media_item = media_item
		self.process = None 
		self.server = server

	def play(self):
		print('{}: Playing {} (Duration: {})'.format(get_time(),self.media_item, self.media_item.duration_readable))

		in1 = ffmpeg.input(self.media_item.path)
		v1 = ffmpeg.filter(in1['v'],'scale', '640x480')
		a1 = in1['a']
		joined = ffmpeg.concat(v1,a1,v=1,a=1)
		self.ff = ffmpeg.output(joined,
								 'pipe:', vcodec='h264', aspect='640:480',
								  preset='ultrafast', hls_allow_cache=0, hls_list_size=5, hls_time=1, format='hls', pix_fmt='yuv444p')

		self.cmd = ['ffmpeg']+ffmpeg.get_args(self.ff)

		self.process = subprocess.Popen(self.cmd, stdout=self.server.stdin, stderr=devnull)

		# self.process = ffmpeg.run_async(self.ff, pipe_stdout=True, quiet=True)

		# self.process = (
		# 			    ffmpeg
		# 			    .input(self.media_item.path)
		# 			    .output('pipe:', vcodec='h264', aspect='640:480', preset='ultrafast', format='mpeg', pix_fmt='yuv444p')
		# 			    .run_async(pipe_stdout=True, quiet=True)
		# )
		self.process.wait()

	def stop(self):
		self.process.terminate()  
