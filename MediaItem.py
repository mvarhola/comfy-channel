import pymediainfo
import datetime

class MediaItem:

    def __init__(self, path):
        self.path = path
        self.media_info = pymediainfo.MediaInfo.parse(self.path, library_file="libmediainfo.dylib")

        self.title = self.media_info.tracks[0].other_file_name[0]
        self.duration = self.media_info.tracks[0].duration
        self.duration_readable = datetime.timedelta(milliseconds=self.duration) 
        self.file_extension = self.media_info.tracks[0].file_extension

    def __str__(self):
    	return self.path