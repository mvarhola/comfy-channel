import ffmpeg
import subprocess
import Logger
import Config as c

devnull = subprocess.DEVNULL

class Server:

	def __init__(self, output):
		self.ff = ''
		self.process = None 
		self.output = output

	def start(self):
		Logger.LOGGER.log(Logger.TYPE_INFO, 'Starting Server, output to: {}'.format(self.output))
		
		in1 = ffmpeg.input('pipe:')
		v1 = ffmpeg.drawtext(in1['v'],'%{localtime:%R}',
								x=c.SERV_DRAWTEXT_X,
								y=c.SERV_DRAWTEXT_Y,
								escape_text=False,
								shadowcolor=c.SERV_DRAWTEXT_SHADOW_COLOR,
								shadowx=c.SERV_DRAWTEXT_SHADOW_X, 
								shadowy=c.SERV_DRAWTEXT_SHADOW_Y,
								fontsize=c.SERV_DRAWTEXT_FONT_SIZE, 
								fontfile=c.SERV_DRAWTEXT_FONT_FILE, 
								fontcolor=c.SERV_DRAWTEXT_FONT_COLOR
							)
		a1 = in1['a']
		joined = ffmpeg.concat(v1,a1,v=1,a=1)		

		self.ff = ffmpeg.output(joined, self.output, vcodec='h264', 
								aspect=c.SERV_OUTPUT_ASPECT, 
								crf=c.SERV_OUTPUT_CRF, 
								preset=c.SERV_OUTPUT_PRESET, 
								format='flv', 
								pix_fmt='yuv444p'
								)

		self.cmd = ['ffmpeg','-re']+ffmpeg.get_args(self.ff)
		self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=devnull, stderr=devnull)
		return self.process

	def stop(self):
		print("Stopping Server")
		self.process.terminate()
