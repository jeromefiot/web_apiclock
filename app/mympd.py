# -*- coding: utf-8 -*-

from mpd import MPDClient
import time
import argparse
import podcastparser
import urllib
import pprint


class player():

    """Play arg "radio" in local HTML player."""

    def __init__(self):
        """Connection init."""
        self.client = MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)

    def clear(self):
        """Clear player playlist."""
        self.client.clear()

    def play(self, media):
        """Start player with media(url) arg."""
        self.client.clear()
        if media:
            self.client.add(media)
            self.client.setvol(60)
            self.client.play()

    def podlist(self, media):
        """Get podcast infos(parsed)."""
        parsed = podcastparser.parse(media, urllib.urlopen(media))
        return parsed

    def stop(self):
        """Stop player."""
        self.client.stop()

    def volup(self, n=10):
        """Set player volume up."""
        status = self.client.status()
        nvol = int(status['volume']) + n
        if nvol > 100:
            nvol = 100
        self.client.setvol(nvol)

    def voldown(self, n=10):
        """Set player volume down."""
        status = self.client.status()
        volume = status['volume']
        nvol = int(volume) - n
        if nvol < 0:
            nvol = 0
        self.client.setvol(nvol)
        print "Volume : %d" % nvol

    def status(self):
        """Get player status."""
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
        """Verify player playing."""
        status = self.status()
        if status['state'] == 'stop':
            return False
        else:
            return True


def main():
    """Playing media."""
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
