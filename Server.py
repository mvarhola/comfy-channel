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
		v1 = ffmpeg.drawtext(in1['v'],'%{localtime:%R}', x=25, y=25, escape_text=False, fontsize=40, fontfile='fonts/ProNW4.ttc', fontcolor='white')
		a1 = in1['a']
		joined = ffmpeg.concat(v1,a1,v=1,a=1)		

		self.ff = ffmpeg.output(joined, self.output, vcodec='h264', aspect='640:480', crf='28', preset='ultrafast', 
								format='flv', pix_fmt='yuv444p')

		self.cmd = ['ffmpeg','-re']+ffmpeg.get_args(self.ff)
		self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=devnull, stderr=devnull)
		return self.process

	def stop(self):
		print("Stopping Server")
		self.process.terminate()
