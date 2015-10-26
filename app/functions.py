from crontab import CronTab
from mpd import MPDClient
from threading import Thread
import time
import datetime
import os, sys

#get current environment variable for crontab commands
env_path = os.environ['VIRTUAL_ENV']
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
cron_command = env_path + '/bin/python ' + script_path + '/mpdplay.py'

newcron = CronTab(user=True)


class Snooze(Thread):
    """Thread Snooze"""
    def __init__(self, radiosnooze, minutessnooze):
        Thread.__init__(self)
        self.radio = radiosnooze
        self.duree = minutessnooze*60
        client = MPDClient()

    def run(self):
        """lance jouerMPD patiente le temps minutesnooze puis stop MDP"""
        jouerMPD(self.radio)
        #fin = time.time() + self.duree # l'heure actuelle + duree (en secondes depuis epoch)
        print self.duree
        time.sleep(self.duree)
        stopMPD()


def addcronenvoi(monalarme):
    job = newcron.new(command=cron_command + ' ' + monalarme['path'],
        comment='Alarme ID:' + str(monalarme['id']))
    jours = ",".join(map(str, monalarme['jours']))
    job.setall(
        monalarme['minute'],
        monalarme['heure'],
        '*',
        '*',
        jours)

    job.enable()
    try:
        newcron.write()
        return 0
    except:
        return 1


def removecron(idalarm):
    newcron.remove_all(comment='Alarme ID:'+str(idalarm))
    newcron.write()

def getpodcasts():
    #recup les podcats du user
    podcasts = Music.query.filter(and_(Music.music_type=='2', Music.users==current_user.id)).all()
    listepodcast = []
    #recup pour chaque podcast les url de ts les emissions
    for emission in podcasts:
        d = feedparser.parse(emission.url)
        emissions=[(d.entries[i]['title'],d.entries[i].enclosures[0]['href']) for i,j in enumerate(d.entries)]
        listepodcast.append(emissions)
    return listepodcast

def jouerMPD(path ='http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3'):
    """ joue mpd avec url en playlist  """
    client = MPDClient()               # create client object
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)  # connect to localhost:6600
    client.clear()
    client.add(path)
    client.play()

def stopMPD():
    """  stop MPD """
    client = MPDClient()               # create client object
    client.connect("localhost", 6600)  # connect to localhost:6600
    client.clear()
    client.stop()
    client.close()
    client.disconnect()                # disconnect from the server


def snooze(radiosnooze, minutessnooze):
    """cree un thread Snooze et le lance"""
    thr_snooze = Snooze(radiosnooze, minutessnooze)
    thr_snooze.start()
