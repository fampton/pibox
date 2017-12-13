#!/usr/bin/env python

import redis
import vlc

import signal
import sys
import time

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False

signal.signal(signal.SIGINT, end_read)

r = redis.Redis()
album_name = sys.argv[1]

def get_album(album_name):
    album_list = []
    for key in r.keys():
        if album_name in r.get(key):
            if r.get(key).endswith('mp3'):
                album_list.append(key)
    return album_list

album = [r.get(key) for key in get_album(album_name)]
album = sorted(album)[:1]
album_playlist = [vlc.Media(x) for x in album]

l = vlc.MediaList(album_playlist)
p = vlc.MediaListPlayer()
p.set_media_list(l)

p.play()
while p.is_playing():
    time.sleep(0.4)
    continue
else:
    sys.exit()


