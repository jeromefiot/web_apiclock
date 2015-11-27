import urllib
import feedparser
import os

from flask import render_template, redirect, request, url_for, \
                  flash, current_app
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from mpd import MPDClient

from . import radio
from .forms import AddMusicForm, PlayRadio
from .. import db
from ..models import Music
from ..decorators import admin_required
from ..functions import jouerMPD, stopMPD, connectMPD


@radio.route('/', methods=['GET', 'POST'], defaults={'action': 0, 'radioe': 0})
@radio.route('/<int:action>/<int:radioe>', methods=['GET', 'POST'])
@login_required
@admin_required
def index(action, radioe):
    """Display user's radio and form to add medias and control radios."""
    radio = Music.query.filter(and_(Music.music_type == '1',
                               Music.users == current_user.id)).all()
    form = AddMusicForm()
    form2 = PlayRadio()
    connectMPD()
    client = MPDClient()

    if form.validate_on_submit() and form.music_type.data == '1':
        """Radio type added in bdd."""
        radio = Music(name=form.name.data,
                      url=form.url.data,
                      description=form.description.data,
                      music_type=form.music_type.data,
                      users=current_user.id)
        db.session.add(radio)
        db.session.commit()
        flash('Radio has been added.')
        return redirect(url_for('.index'))

    elif form.validate_on_submit() and form.music_type.data == '2':
        """ if Feed (podcast) added then redirect to linked shows """
        url = form.url.data
        d = feedparser.parse(url)

        podcast = Music(name=form.name.data,
                        url=form.url.data,
                        img=d['feed']["image"]["url"],
                        description=form.description.data,
                        music_type=form.music_type.data,
                        users=current_user.id)
        db.session.add(podcast)
        db.session.commit()

        flash('Podcast ok')
        return render_template('radio/shows.html', podcast=form.name.data)

    elif action is 1 and radioe is not 0:
        """Action = 1 > Remove media which id = radioe."""
        radiodel = Music.query.filter(Music.id == radioe).first()
        db.session.delete(radiodel)
        db.session.commit()
        if radiodel.music_type == 3:
            os.remove(current_app.config['UPLOAD_FOLDER']+name)
        flash('Delete successful !')
        return redirect(url_for('.index'))

    elif action is 2:
        """ action = 2 > play radio (MPD) """
        client.clear()
        client.add('http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3')
        client.play()
        return redirect(url_for('.index'))

    elif action is 3:
        """ action = 3 > stop radio (MPD) """
        client.clear()
        client.stop()
        client.close()
        return redirect(url_for('.index'))

    return render_template('radio/radio.html',
                           form=form, form2=form2, radios=radio)


@radio.route('/edit/<int:radioedit>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(radioedit):
    """Edit Radio form."""
    radioe = Music.query.filter(Music.id == radioedit).first()
    radio = Music.query.filter(and_(Music.music_type == '1',
                               Music.users == current_user.id)).all()
    form = AddMusicForm()

    if form.validate_on_submit():
        radioe.name = form.name.data
        radioe.url = form.url.data
        radioe.description = form.description.data
        db.session.add(radioe)
        flash('Radio has been updated')

    form.name.data = radioe.name
    form.url.data = radioe.url
    form.description.data = radioe.description
    return render_template('radio/radio.html', form=form, radios=radio)


@radio.route('/podcast/', methods=['GET', 'POST'], defaults={'action': 'rien'})
@radio.route('/podcast/<action>', methods=['GET', 'POST'])
@login_required
@admin_required
def podcast(action):
    """Display podcasts subscription list for current user."""
    podcasts = Music.query.filter(and_(Music.music_type == '2',
                                  Music.users == current_user.id)).all()

    if action == "unsubscribe":
        idmusic = request.args.get('music_id')
        podcast = Music.query.filter(Music.id == idmusic).first()
        db.session.delete(podcast)
        db.session.commit()
        flash('Podcast has been deleted')
        return redirect(url_for('.podcast'))

    elif action == "show":
        idmusic = request.args.get('music_id')
        podcast = Music.query.filter(Music.id == idmusic).first()
        d = feedparser.parse(podcast.url)
        shows = [(d.entries[i]['title'], d.entries[i].enclosures[0]['href'])
                 for i, j in enumerate(d.entries)]
        return render_template('radio/shows.html', shows=shows,
                               titre=podcast.name)

    elif action == "donwload":
        """ Download podcast as music type media in music directory """
        up_dir = "/home/pi/apiclock/app/static/musique/"
        urlmusic = request.args.get('urlpodcast')
        name_podcast = 'PODCAST_' + request.args.get('nompodcast')
        try:
            stock_music = urllib.urlretrieve(urlmusic, up_dir + name_podcast)
            # TO ADD : check the disk space
            addmusic = Music(
                    name=name_podcast,
                    url="http://jeromefiot.fr/static/musique/" + name_podcast,
                    music_type=3,
                    users=current_user.id)
            db.session.add(addmusic)
            db.session.commit()
            flash('Your podcast has been download in your Music')
        except:
                flash('Error adding your podcast to your music')
        return redirect(url_for('.podcast'))

    return render_template('radio/podcast.html', podcasts=podcasts)


@radio.route('/music', methods=['GET', 'POST'])
@login_required
@admin_required
def music():
    """Display user's music."""
    musics = Music.query.filter(and_(Music.music_type == '3',
                                Music.users == current_user.id)).all()

    return render_template('radio/music.html', radios=musics)


@radio.route('/local/<path:radio>')
@login_required
@admin_required
def local(radio):
    """Play arg "radio" in local HTML player."""
    return render_template('radio/player.html', music=radio)


@radio.route('/distant/<path:radio>')
@login_required
@admin_required
def distant(radio):
    """Play arg "radio" in MPD (distant player)."""
    if radio == 'stop':
        stopMPD()
        return redirect(url_for('.index'))

    jouerMPD(radio)
    return render_template('radio/distant.html')
