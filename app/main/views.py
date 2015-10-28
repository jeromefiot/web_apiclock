# coding: utf-8

from flask import render_template, redirect, url_for, abort, flash, request
from flask.ext.login import login_required, current_user
from flask.ext.mail import Mail, Message
from sqlalchemy.sql import and_
from crontab import CronTab
from mpd import MPDClient
from threading import Thread
import os

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, playerForm, addAdmin, ContactForm,\
    snoozeForm
from .. import db, mail
from ..models import Role, User, Alarm, Music
from ..decorators import admin_required
from ..functions import jouerMPD, snooze

#========================================
#============ PAGES PUBLIQUES ===========
#========================================

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('public/contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender='contact@example.com', recipients=['j_fiot@hotmail.com'])
            msg.body = """
            From: %s &lt;%s&gt;
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('public/contact.html', success=True)
        
    elif request.method == 'GET':
        return render_template('public/contact.html', form=form)


@main.route('/apiclock')
def apiclock():
    
    return render_template('index.html')


@main.route('/presentation')
def presentation():
    
    return render_template('public/presentation.html')


@main.route('/blog')
def blog():
    
    return render_template('public/blog.html')


@main.route('/thanks')
def thanks():
    
    return render_template('public/thanks.html')


@main.route('/cv')
def cv():
    
    return render_template('public/cv.html')


@main.route('/installation')
def installation():
    
    return render_template('public/installation.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

#========================================
#=========== PAGES SEMI PRIVEES =========
#========================================

@main.route('/', methods=['GET', 'POST'])
def index():
    client = MPDClient()               # create client object
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)
    
    if 'play' in request.form:
        # connect to localhost:6600
        client.add('http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3')
        client.play()
    elif 'stop' in request.form:
        client.stop()
        client.close()
    return render_template('index.html')

#========================================
#============= PAGES PRIVEES ============
#========================================

@main.route('/dashboard', methods=['GET', 'POST'], defaults = {'action':4})
@main.route('/dashboard/<action>/<musique>', methods=['GET', 'POST'])
@login_required
@admin_required
def dashboard(action, musique="http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3"):
    
    client = MPDClient()
    client.connect("localhost", 6600)

    form1 = playerForm(prefix="form1")
    formsnooze = snoozeForm()
    
    if formsnooze.submitsnooze.data:
        """recup radio par id et retourne url a jouerMPD()"""
        radiosnooze = formsnooze.radiosnooze.data
        radiosnooze = Music.query.filter(Music.id==radiosnooze).first()
        radiosnooze = radiosnooze.url
        minutessnooze = int(formsnooze.minutessnooze.data)
        snooze(radiosnooze, minutessnooze)
        return redirect(url_for('.dashboard'))
    
    elif form1.submit.data:
        """suivant le type de media recup id de celui ci puis requete pour url"""
        radio = form1.radio.data
        media = Music.query.filter(Music.id==radio).first()
        jouerMPD(media.url)
        return redirect(url_for('.dashboard'))
    
    # get in GET the action's param
    elif action == '1':
        """play the urlmedia passed in args with a 110% volum"""
        os.system('amixer sset PCM,0 92%')
        client.stop()
        client.clear()
        client.add("http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3")
        client.play()
        return redirect(url_for('.dashboard'))
    elif action == '0':
        """stop and clear MPD playlist"""
        client.clear()
        client.stop()
        client.close()
        return redirect(url_for('.dashboard'))
    elif action == '2':
        """Increase volume by 3dB"""
        os.system('amixer sset PCM,0 3dB+')
        return redirect(url_for('.dashboard'))
    elif action == '3':
        """Decrease volume by 3dB"""
        os.system('amixer sset PCM,0 3dB-')
        return redirect(url_for('.dashboard'))
    else :
        return render_template('dashboard.html', form1=form1, formsnooze=formsnooze)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    user = User.query.all()
    if request.args.get('id'):
        print 'yes'
        userid = request.args.get('id')
        print userid
        userd = User.query.filter(User.id==userid).first()
        db.session.delete(userd)
        db.session.commit()
        flash('The user has been deleted.')
        return redirect(url_for('.users', users=user))
    return render_template('users.html', users=user)


@main.route('/admin_stuff', methods=['GET', 'POST'])
@main.route('/admin_stuff/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_stuff():
    form = addAdmin()
    with open('/home/pi/apiclock/admin.txt', 'a+') as f:
        if form.validate_on_submit():
            ajout = form.about_me.data
            f.write(ajout+'\n')
            return redirect(url_for('.admin_stuff'))
        data = f.readlines()
        data = [str(i)+'/'+str(val) for i, val in enumerate(data)]

    return render_template('admin_stuff.html', form=form, data=data)
