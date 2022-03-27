import subprocess
from datetime import datetime

import ffmpeg
import psutil

import Config as c
import Logger

CLIENT_DEBUG = False
devnull = subprocess.DEVNULL


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


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
            Logger.LOGGER.log(Logger.TYPE_INFO, 'Playing upnext v:{} a:{} (Duration: {})'.format(
                self.media_item.video_path, self.media_item.audio_path, self.media_item.duration_readable))

            in1 = ffmpeg.input(self.media_item.video_path)
            in2 = ffmpeg.input(self.media_item.audio_path)
            v1 = ffmpeg.filter(in1['v'], 'scale', c.CLIENT_VIDEO_SCALE)
            v1 = ffmpeg.drawtext(v1, '{}'.format(self.media_item.overlay_text),
                                 x=c.CLIENT_DRAWTEXT_X,
                                 y=c.CLIENT_DRAWTEXT_Y,
                                 escape_text=False,
                                 shadowcolor=c.CLIENT_DRAWTEXT_SHADOW_COLOR,
                                 shadowx=c.CLIENT_DRAWTEXT_SHADOW_X,
                                 shadowy=c.CLIENT_DRAWTEXT_SHADOW_Y,
                                 fontsize=c.CLIENT_DRAWTEXT_FONT_SIZE,
                                 fontfile=c.CLIENT_DRAWTEXT_FONT_FILE,
                                 fontcolor=c.CLIENT_DRAWTEXT_FONT_COLOR)

            a1 = in1['a']
            a2 = in2['a']
            audio_join = ffmpeg.filter([a1, a2], 'amix', duration="first")

            output_stream = ffmpeg.concat(v1, audio_join, v=1, a=1)

        else:
            Logger.LOGGER.log(Logger.TYPE_INFO, 'Playing v:{} (Duration: {})'.format(
                self.media_item, self.media_item.duration_readable))

            in1 = ffmpeg.input(self.media_item.video_path)
            v1 = ffmpeg.filter(in1['v'], 'scale', c.CLIENT_VIDEO_SCALE)
            if (c.CLIENT_ENABLE_DEINTERLACE):
                v1 = ffmpeg.filter(v1, 'yadif')
            a1 = in1['a']
            output_stream = ffmpeg.concat(v1, a1, v=1, a=1)

        self.ff = ffmpeg.output(output_stream,
                                'pipe:',
                                vcodec=c.CLIENT_VCODEC,
                                aspect=c.CLIENT_ASPECT,
                                flags=c.CLIENT_FLAGS,
                                g=c.CLIENT_G,
                                acodec=c.CLIENT_ACODEC,
                                strict=c.CLIENT_STRICT,
                                ab=c.CLIENT_AUDIO_BITRATE,
                                ar=c.CLIENT_AUDIO_RATE,
                                preset=c.CLIENT_PRESET,
                                hls_allow_cache=c.CLIENT_HLS_ALLOW_CACHE,
                                hls_list_size=c.CLIENT_HLS_LIST_SIZE,
                                hls_time=c.CLIENT_HLS_TIME,
                                format=c.CLIENT_FORMAT,
                                pix_fmt=c.CLIENT_PIX_FMT)

        self.cmd = ['ffmpeg']+ffmpeg.get_args(self.ff)

        self.process = subprocess.Popen(
            self.cmd, stdout=self.server.stdin, stderr=(None if CLIENT_DEBUG else devnull))
        try:
            flex = c.CLIENT_FLEX  # Number of seconds of extra time before timeout
            timeout = (self.media_item.duration/1000) # Content length in seconds
            self.process.wait(timeout=timeout+flex)
        except subprocess.TimeoutExpired:
            Logger.LOGGER.log(
                Logger.TYPE_ERROR, 'Taking longer to play than expected, killing current item')
            kill(self.process.pid)
            self.process.returncode = 0

        # returncode 0 if process exited without problems, 1 for general error
        return self.process.returncode

    def stop(self):
        self.process.terminate()
