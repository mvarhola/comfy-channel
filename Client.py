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
		self.media_type = media_item.media_type
		self.process = None 
		self.server = server

	def play(self):
		output_stream = None

		if self.media_type == "upnext":
			print('{}: Playing upnext v:{} a:{} (Duration: {})'.format(get_time(), self.media_item.video_path, self.media_item.audio_path, self.media_item.duration_readable))
			
			in1 = ffmpeg.input(self.media_item.video_path)
			in2 = ffmpeg.input(self.media_item.audio_path)
			v1 = ffmpeg.filter(in1['v'],'scale', '640x480')
			v1 = ffmpeg.drawtext(v1,'{}'.format(self.media_item.overlay_text), x=25, y=113, escape_text=False, fontsize=24, fontfile='fonts/ProNW4.ttc', fontcolor='white')

			a1 = in1['a']
			a2 = in2['a']
			audio_join = ffmpeg.filter([a1,a2],'amix',duration="first")
					
			output_stream = ffmpeg.concat(v1,audio_join,v=1,a=1)

		else: 
			print('{}: Playing v:{} (Duration: {})'.format(get_time(), self.media_item, self.media_item.duration_readable))
			
			in1 = ffmpeg.input(self.media_item.video_path)
			v1 = ffmpeg.filter(in1['v'],'scale', '640x480')
			a1 = in1['a']
			output_stream = ffmpeg.concat(v1,a1,v=1,a=1)

		
		self.ff = ffmpeg.output(output_stream,
								'pipe:', vcodec='h264', aspect='640:480', flags="+cgop", g=30, 
								acodec='aac', strict='1', ab='168k', ar=44100,
								preset='ultrafast', hls_allow_cache=0, hls_list_size=5, hls_time=0.1, format='hls', pix_fmt='yuv444p')

		self.cmd = ['ffmpeg']+ffmpeg.get_args(self.ff)

		self.process = subprocess.Popen(self.cmd, stdout=self.server.stdin, stderr=devnull)
		self.process.wait()

	def stop(self):
		self.process.terminate()  
