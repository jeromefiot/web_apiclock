from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from mpd import MPDClient
import os.path
import feedparser
from . import alarm
from .forms import AddMusicForm
from .. import db
from ..models import User, Music
from ..decorators import admin_required

#============= FONCTIONS ============

def addcronenvoi(idalarm):
    newcron=CronTab()
    job=newcron.new(command='/home/pi/.virtualenvs/apiclock/bin/python /home/pi/apiclock/alarm.py radioreveil', comment='Alarme ID:'+str(idalarm))
    job.hour.every(2)
    job.enable()
    newcron.write()

def jouerMPD(path):
    """   """
    client = MPDClient()               # create client object
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)  # connect to localhost:6600
    client.add(path)
    client.play()
    #client.close()                     # send the close command
    #client.disconnect()                # disconnect from the server

#====================================

@alarm.route('/', methods=['GET', 'POST'], defaults = {'action':0, 'radioe':0})
@alarm.route('/<int:action>/<int:radioe>', methods=['GET', 'POST'])
@login_required
def index(action, radioe):
    radio = Music.query.filter(and_(Music.music_type=='1', Music.users==current_user.id)).all()
    form = AddMusicForm()

    if form.validate_on_submit() and form.music_type.data=='1':
        # if Radio type added insert radio in bdd
        radio = Music(name=form.name.data,
                      url=form.url.data,
                      description=form.description.data,
                      music_type=form.music_type.data,
                      users=current_user.id)
        db.session.add(radio)
        db.session.commit()
        flash('Radio has been added.')
        return redirect(url_for('.index'))
    
    elif form.validate_on_submit() and form.music_type.data=='2':
        # if Feed (podcast) added then redirect to linked shows
        url=form.url.data
        d = feedparser.parse(url)
        #podcast = d['feed']["image"]["url"]
        #podcast = Podcast(titre=d['feed']["subtitle"],
        #                  lien=d['feed']["link"],
        #                  img=d['feed']["url"]
        #                 )
        podcast = Music(name=form.name.data,
                      url=form.url.data,
                      img=d['feed']["image"]["url"],
                      description=form.description.data,
                      music_type=form.music_type.data,
                      users=current_user.id)
        db.session.add(podcast)
        db.session.commit()
        
        flash('Podcast ok')
        return render_template('alarm/shows.html', podcast=form.name.data)
    
    elif action is 1 and radioe is not 0 :
        """ action = 1 > SUPPRESSION de la radio ayant l'id radio passe par le param radioe """
        radiodel = Music.query.filter(Music.id==radioe).first()
        db.session.delete(radiodel)
        db.session.commit()
        flash('Radio has been deleted')
        return redirect(url_for('.index'))

    return render_template('alarm/radio.html', form=form, radios=radio)


@alarm.route('/edit/<int:radioedit>', methods=['GET', 'POST'])
@login_required
def edit(radioedit):
    radioe = Music.query.filter(Music.id==radioedit).first()
    radio = Music.query.filter(and_(Music.music_type=='1', Music.users==current_user.id)).all()
    form = AddMusicForm()
    
    if form.validate_on_submit():
        radioe.name=form.name.data
        radioe.url=form.url.data
        radioe.description=form.description.data
        db.session.add(radioe)
        flash('Radio has been updated')
        
    form.name.data=radioe.name
    form.url.data=radioe.url
    form.description.data=radioe.description
    return render_template('alarm/radio.html', form=form, radios=radio)


@alarm.route('/podcast/', methods=['GET', 'POST'], defaults = {'action':'rien'})
@alarm.route('/podcast/<action>', methods=['GET', 'POST'])
@login_required
def podcast(action):
    """ Display podcasts subscription list for current user"""
    if action == 'rien':
        podcasts = Music.query.filter(and_(Music.music_type=='2', Music.users==current_user.id)).all()
        test = 'rien'
        
    elif action == "unsubscribe":
        idmusic = request.args.get('music_id')
        podcast = Music.query.filter(Music.id==idmusic).first()
        db.session.delete(podcast)
        db.session.commit()
        flash('Podcast has been deleted')
        return redirect(url_for('.podcast'))
                        
    elif action == "show":
        idmusic = request.args.get('music_id')
        podcast = Music.query.filter(Music.id==idmusic).first()
        d = feedparser.parse(podcast.url)
        shows=[(d.entries[i]['title'],d.entries[i].enclosures[0]['href']) for i,j in enumerate(d.entries)]
        return render_template('alarm/shows.html', shows=shows)
        
    return render_template('alarm/podcast.html', podcasts=podcasts, test=test)


@alarm.route('/local/<path:radio>')
@login_required
def local(radio):
    return render_template('alarm/player.html', music=radio)


@alarm.route('/distant/<path:radio>')
@login_required
def distant(radio):
    
    if radio == 'stop':
        client = MPDClient() 
        client.connect("localhost", 6600)
        client.clear()
        client.stop()
        return redirect(url_for('.index'))
        
    jouerMPD(radio)
    return render_template('alarm/distant.html')