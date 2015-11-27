# -*- coding: utf-8 -*-

from mpd import MPDClient
import time
import argparse
import podcastparser
import urllib
import pprint


class player():

    def __init__(self):
        self.client = MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)

    def clear(self):
        self.client.clear()

    def play(self, media):
        self.client.clear()
        if media:
            self.client.add(media)
            self.client.setvol(60)
            self.client.play()

    def podlist(self, media):
        parsed = podcastparser.parse(media, urllib.urlopen(media))
        return parsed

    def stop(self):
        self.client.stop()

    def volup(self, n=10):
        status = self.client.status()
        nvol = int(status['volume']) + n
        if nvol > 100:
            nvol = 100
        self.client.setvol(nvol)

    def voldown(self, n=10):
        status = self.client.status()
        volume = status['volume']
        nvol = int(volume) - n
        if nvol < 0:
            nvol = 0
        self.client.setvol(nvol)
        print "Volume : %d" % nvol

    def status(self):

        status = self.client.status()

        monstatus = {}

        for key, value in status.items():
            monstatus[key] = value.encode('utf-8')

        time.sleep(2)
        maplaylist = self.client.playlistid()
        try:
            for key, value in maplaylist[0].items():
                monstatus[key] = value.decode('utf-8')
        except:
            pass
        return monstatus, maplaylist

    def is_playing(self):
        status = self.status()
        if status['state'] == 'stop':
            return False
        else:
            return True


def main():

    parser = argparse.ArgumentParser(
    description="This script play a given media on the mpd (local) server")
    parser.add_argument("-c",
        choices=['play', 'stop', 'status', 'volup', 'voldown', 'pod'],
        required=True)
    parser.add_argument("-u", help="url to play")

    args = parser.parse_args()

    media = args.u
    command = args.c

    myplayer = player()
    if command == 'play':
        if media is not None:
            myplayer.play(media)
        else:
            print "You must enter a media url/path to play"
    elif command == 'stop':
        myplayer.stop()
    elif command == 'volup':
        myplayer.volup()
    elif command == 'voldown':
        myplayer.voldown()
    elif command == 'status':
        state = myplayer.status()
        for cle, val in state.items():
            print cle + " : " + val
    elif command == 'podlist':
        parsed = podcastparser.parse(media, urllib.urlopen(media))
        pprint.pprint(parsed)


if __name__ == "__main__":
    main()