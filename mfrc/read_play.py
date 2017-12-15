#!/usr/bin/env python
# -*- coding: utf8 -*-

import ast
import pyA20.gpio as GPIO
import MFRC522
import redis
import signal
import sys
import time
import vlc

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    print "Ctrl+C captured, exiting."
    p.stop()
    sys.exit(0)

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            mread = MIFAREReader.MFRC522_Read(8)
            print mread
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print "Authentication error"

        r = redis.Redis()
        
        data = ''.join('{:02x}'.format(x) for x in mread)
        print data
        print type(data)
        album = r.get(data)
        album = ast.literal_eval(album)
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

