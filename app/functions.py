import os, sys, time

from crontab import CronTab
from mpd import MPDClient
from threading import Thread

from . import db, login_manager
from .models import Alarm, Music


#get current environment variable for crontab commands
env_path     = os.environ['VIRTUAL_ENV']
script_path  = os.path.dirname(os.path.realpath(sys.argv[0]))
cron_command = env_path + '/bin/python ' + script_path + '/mpdplay.py'
newcron      = CronTab(user=True)


class Snooze(Thread):
    """Activate a thread for Snooze function"""
    def __init__(self, radiosnooze, minutessnooze):
        Thread.__init__(self)
        self.radio = radiosnooze
        self.duree = minutessnooze*60
        client     = MPDClient()

    def run(self):
        """start jouerMPD stop during minutesnooze then stop MPD"""
        jouerMPD(self.radio)
        time.sleep(self.duree)
        stopMPD()


def addcronenvoi(monalarme):
    """ transform and add alarm in crontab with a 2h duration"""
    alarmduration = int(monalarme['heure'])+2

    job = newcron.new(command=cron_command + ' ' + monalarme['path'],
                      comment='Alarme ID:' + str(monalarme['id']))
    jours = ",".join(map(str, monalarme['jours']))
    job.setall(
        monalarme['minute'],
        "{}-{}".format(monalarme['heure'], alarmduration),
        #str(monalarme['heure'])+'-'+str(alarmduration),
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


def statealarm(idalarm):
    """Find the existing alarm by id in crontab comment and activate or deactivate it """
    actionalarm = newcron.find_comment('Alarme ID:'+str(idalarm))
    actionalarm = next(actionalarm)
    alarms      = Alarm.query.filter(Alarm.id==idalarm).first()
    if alarms.state == 1:    
        alarms.state = 0
        actionalarm.enable(False)
    else :
        alarms.state = 1
        actionalarm.enable()
    newcron.write()
    db.session.commit()


def getpodcasts():
    """Get all emissions for the current_user podcast"""
    podcasts = Music.query.filter(and_(Music.music_type=='2', Music.users==current_user.id)).all()
    listepodcast = []
    #Get URL of all emissions off the podcast
    for emission in podcasts:
        d         = feedparser.parse(emission.url)
        emissions =[(d.entries[i]['title'],d.entries[i].enclosures[0]['href']) for i,j in enumerate(d.entries)]
        listepodcast.append(emissions)
    return listepodcast

def jouerMPD(path ='http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3'):
    """ play mpd with url playlist in arg """
    client             = MPDClient()   # create client object
    client.timeout     = 10            # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)  # connect to localhost:6600
    client.clear()
    client.add(path)
    client.play()

def stopMPD():
    """ Stop MPD """
    client = MPDClient()               # create client object
    client.connect("localhost", 6600)  # connect to localhost:6600
    client.clear()
    client.stop()
    client.close()
    client.disconnect()                # disconnect from the server


def snooze(radiosnooze, minutessnooze):
    """Create a Snooze thread and start it"""
    thr_snooze = Snooze(radiosnooze, minutessnooze)
    thr_snooze.start()
