from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from crontab import CronTab
import feedparser

from . import alarm
from .forms import addAlarmForm
from .. import db
from ..models import Role, User, Alarm, Music
from ..decorators import admin_required

#============= FONCTIONS ============

newcron=CronTab()

def addcronenvoi(idalarm,jourscron,heurescron,minutescron,frequence,path):
    job=newcron.new(command='/home/pi/.virtualenvs/apiclock/bin/python /home/pi/apiclock/mpdplay.py '+path, comment='Alarme ID:'+str(idalarm))
    job.hour.on(heurescron)
    job.minute.on(minutescron)
    job.dow.on(jourscron)
    #job.hour.during(1,0).every(1)
    if frequence == '6':
        job.every_reboot()
    elif frequence =='dows':
        job.dow.on(jourscron)
    elif frequence == 'frequency_per_year':
        job.frequency_per_year() == 1
    else:
        pass
    job.enable()
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

#==============

@alarm.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():    
    alarms = Alarm.query.filter(Alarm.users==current_user.id).all()
    radios = Music.query.filter(and_(Music.music_type=='1', Music.users==current_user.id)).all()
    form = addAlarmForm()

    if form.validate_on_submit():
        namecron = form.name.data
        recupjours = dict((key, request.form.getlist(key)) for key in request.form.keys())
        jourscron = ', '.join(recupjours['jours'])
        heurescron = form.heures.data
        minutescron = form.minutes.data
        frequencecron = form.frequence.data
        # result de la requete et recup le champ URL
        path = form.Radio.data.url
        
        alarme = Alarm(namealarme=namecron,
                      days=jourscron,
                      startdate=str(heurescron)+':'+str(minutescron),
                      frequence=frequencecron,
                      users=current_user.id)
        db.session.add(alarme)
        db.session.commit()

        # setting up crontab
        addcronenvoi(alarme.id,jourscron,heurescron,minutescron,frequencecron,path)
        flash('Your alarm has been programed.')
        
    return render_template("alarm/alarm.html", form=form, user=current_user, alarms=alarms, radios=radios)