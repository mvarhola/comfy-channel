import os
import random
from datetime import timedelta
from pymediainfo import MediaInfo

import Logger
import Config as c
from MediaItem import MediaItem

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield os.path.join(path, f)

def listdir_file_walk(dir):
    directory_listing = []

    for path, dirs, files in os.walk(dir):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for name in files:
            directory_listing += [os.path.join(path, name)]

    return directory_listing


def gen_playlist(dir, num_files=None):
    Logger.LOGGER.log(Logger.TYPE_INFO,
                      'Generating playlist from directory: {}'.format(dir))
    playlist = []
    directory_listing = []

    # If no num_files is passed, just use whole dir
    # (Used mainly by generating the bump playlist)
    if num_files == None:
        num_files = len(directory_listing)

    # https://stackoverflow.com/questions/2909975/python-list-directory-subdirectory-and-files
    for path, dirs, files in os.walk(dir):
        # Filtering dot files and folders and extensions commonly used for subtitles
        files = [f for f in files if (not f[0] == '.') and (not f.split('.')[-1] in ['srt', 'ass', 'idx', 'sub'])]
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for name in files:
            directory_listing += [os.path.join(path, name)]

    random.shuffle(directory_listing, random.SystemRandom().random)
    for i in directory_listing[:num_files]:
        playlist.append(MediaItem(i))

    return playlist


def gen_upnext(video_dir, audio_dir=None, playlist=None, info_file=None):
    video_file = None
    audio_file = None
    info_text = None

    video_file = random.choice(list(listdir_nohidden(video_dir)))
    audio_file = random.choice(listdir_file_walk(audio_dir))

    if playlist:
        info_text = gen_upnext_text(playlist, info_file=info_file, duration=MediaInfo.parse(video_file).tracks[0].duration/1000)

    return MediaItem(video_path=video_file, audio_path=audio_file, media_type="upnext", overlay_text=info_text)


def gen_upnext_text(playlist, info_file=None, duration=0):
    overlay_text = ""
    c.TIME_INDEX += timedelta(seconds=duration) # Upnext Length 

    for i in range(len(playlist)):
        item = playlist[i]
        if i == 0:
            overlay_text += 'Next -' + \
            "  " + item.title + "\n\n"
        else:
            overlay_text += c.TIME_INDEX.strftime("%H:%M") + ' -' + \
            "  " + item.title + "\n\n"
        c.TIME_INDEX += timedelta(seconds=(item.duration/1000))

    if info_file:
        overlay_text += "\n" + get_random_line(info_file)

    return overlay_text


def get_random_line(file):
    file = open(file)
    random_line = random.choice(file.readlines())
    random_line += str("\n")
    file.close()
    return random_line
