import ffmpeg
import subprocess
import Logger
import Config as c

SERVER_DEBUG = False
devnull = subprocess.DEVNULL

# The server consumes the stream from the client and outputs a single continuous stream
# Also adds a clock overlay onto the video


class Server:

    def __init__(self, output):
        self.ff = ''
        self.process = None
        self.output = output
        self.overlay_file = ffmpeg.input(c.OVERLAY_FILE)
        self.overlay_file_outline = ffmpeg.input(c.OVERLAY_FILE_OUTLINE)


    def start(self):
        Logger.LOGGER.log(Logger.TYPE_INFO,
                          'Starting Server, output to: {}'.format(self.output))

        in1 = ffmpeg.input('pipe:')
        v1 = ffmpeg.drawtext(in1['v'], '%{localtime:%R}',
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
        v1 = ffmpeg.overlay(v1, self.overlay_file, x=c.OVERLAY_X, y=c.OVERLAY_Y, loop=1, t=4)
        v1 = ffmpeg.overlay(v1, self.overlay_file_outline, x=c.OVERLAY_X, y=c.OVERLAY_Y, loop=1, t=4)

        a1 = in1['a']
        joined = ffmpeg.concat(v1, a1, v=1, a=1)

        self.ff = ffmpeg.output(joined, self.output, vcodec='h264',
                                aspect=c.SERV_OUTPUT_ASPECT,
                                acodec=c.SERV_OUTPUT_ACODEC,
                                crf=c.SERV_OUTPUT_CRF,
                                preset=c.SERV_OUTPUT_PRESET,
                                format='flv',
                                pix_fmt='yuv420p'
                                )

        self.cmd = ['ffmpeg', '-re']+ffmpeg.get_args(self.ff)
        self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=devnull, stderr=(
            None if SERVER_DEBUG else devnull))
        Logger.LOGGER.log(Logger.TYPE_INFO,
                    'Server Process Created')
        return self.process

    def stop(self):
        print("Stopping Server")
        self.process.terminate()
