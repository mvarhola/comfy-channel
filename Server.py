import ffmpeg
import subprocess
from datetime import datetime

devnull = subprocess.DEVNULL

def get_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Server:

	def __init__(self):
		self.status = "Initialized"
		self.ff = ''
		self.process = None 
		self.output = 'rtmp://localhost/live/mystream'

	def start(self):
		print('{}: Starting Server'.format(get_time()))
		
		in1 = ffmpeg.input('pipe:')
		v1 = ffmpeg.drawtext(in1['v'],'%{localtime:%R}', x=10, y=10, escape_text=False, fontsize=64, fontfile='camcorder.otf', fontcolor='white')
		# v1 = ffmpeg.filter(in1['v'],'scale', '640x480')
		a1 = in1['a']
		joined = ffmpeg.concat(v1,a1,v=1,a=1)
		self.ff = ffmpeg.output(joined, self.output, vcodec='h264', aspect='640:480', crf='28', preset='ultrafast', 
								acodec='aac', strict='1', ab='168k', ar=44100, format='flv', pix_fmt='yuv444p')

		# self.process = ffmpeg.run_async(self.ff, cmd=['ffmpeg','-re'], pipe_stdin=True, quiet=True)
		self.cmd = ['ffmpeg','-re']+ffmpeg.get_args(self.ff)
		self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=devnull, stderr=devnull)

		# self.process = (
		# 			    ffmpeg
		# 			    .input('pipe:')
		# 			    # .drawtext('%{localtime}', x=10, y=10, escape_text=False, fontsize=64, fontfile='camcorder.otf', fontcolor='white')
		# 			    .output(self.output, vcodec='h264', aspect='640:480', crf='28', preset='ultrafast', acodec='aac', strict='1', ab='128k', ar=44100, format='flv', pix_fmt='yuv444p')
		# 			    .run_async(cmd=['ffmpeg','-re'], pipe_stdin=True, quiet=True)
		# )

		return self.process

	def stop(self):
		print("Stopping Server")
		self.process.terminate()
