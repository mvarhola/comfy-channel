import os
import random
from datetime import datetime

import Logger
from MediaItem import MediaItem


def get_time_hm():
    return datetime.now()


def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield os.path.join(path, f)


def gen_playlist(dir, num_files=5):
    Logger.LOGGER.log(Logger.TYPE_INFO,
                      'Generating playlist from directory: {}'.format(dir))
    playlist = []
    directory_listing = []

    # https://stackoverflow.com/questions/2909975/python-list-directory-subdirectory-and-files
    for path, dirs, files in os.walk(dir):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for name in files:
            directory_listing += [os.path.join(path, name)]

    random.shuffle(directory_listing)
    for i in directory_listing[:num_files]:
        playlist.append(MediaItem(i))

    return playlist


def gen_upnext(video_dir, audio_dir=None, playlist=None, info_file=None):
    video_file = None
    audio_file = None
    info_text = None

    video_file = random.choice(list(listdir_nohidden(video_dir)))
    audio_file = random.choice(list(listdir_nohidden(audio_dir)))

    if playlist:
        info_text = gen_upnext_text(playlist, info_file=info_file)

    return MediaItem(video_path=video_file, audio_path=audio_file, media_type="upnext", overlay_text=info_text)


def gen_upnext_text(playlist, info_file=None):
    overlay_text = ""

    time_index = get_time_hm()
    for item in playlist:
        overlay_text += time_index.strftime("%H:%M") + \
            "  " + item.title + "\n\n"
        time_index += item.duration_readable

    if info_file:
        overlay_text += "\n" + get_random_line(info_file)

    return overlay_text


def get_random_line(file):
    file = open(file)
    random_line = random.choice(file.readlines())
    random_line += str("\n")
    file.close()
    return random_line
