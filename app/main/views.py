# coding: utf-8

from flask import render_template, redirect, url_for, abort, flash, request, send_from_directory
from flask.ext.login import login_required, current_user
from flask.ext.mail import Mail, Message
from sqlalchemy.sql import and_
from crontab import CronTab
from mpd import MPDClient
from threading import Thread
import os, pickle
import subprocess
import datetime

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
    
    alarms = Alarm.query.filter_by(users=current_user.id).all()
        
    # load todo list and search for today todo
    f = open('/home/pi/apiclock/admin.txt', 'r')
    data1 = f.readlines()
    today = datetime.datetime.now().strftime('%d-%m-%y')
    listedujour = []
    for element in data1:
        if element[-9:-1] == today:
            # cut end (= date )and remove last element (/) then compare with date
            listedujour.append(element)
        else : 
            pass
    
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
        os.system('amixer sset PCM,0 94%')
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
        return render_template('dashboard.html', form1=form1, formsnooze=formsnooze, alarms=alarms, listedujour=listedujour)


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
    return render_template('admin/users.html', users=user)


@main.route('/diskutil')
@login_required
@admin_required
def diskutil():
    commande = subprocess.Popen("df -h",stdout=subprocess.PIPE,shell=True)
    retour = commande.stdout.readlines()
    
    return render_template('/admin/diskutil.html', test=retour)


@main.route('/admin_stuff', methods=['GET', 'POST'])
@main.route('/admin_stuff/<idline>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_stuff(idline='0'):
    form = addAdmin()
    
    f = open('/home/pi/apiclock/admin.txt', 'r')
    data1 = f.readlines()
    data = [str(i)+'/'+str(val) for i, val in enumerate(data1)]
    today = datetime.datetime.now().strftime('%d-%m-%y')
    
    if form.validate_on_submit():
        f = open('/home/pi/apiclock/admin.txt', 'a+')
        """add line to the admin.txt with number and extract date """
        ajout = form.about_me.data
        # extract date if mentionned ('__') else add tomorow for the date
        if '__' in ajout :
            date_todo = ajout[-8:]
            date_todo = datetime.datetime.strptime(date_todo, '%d-%m-%y').date()
            text_todo = ajout[:-8]
        else:
            text_todo = ajout
            date_todo = datetime.datetime.now()+datetime.timedelta(days=1)
            date_todo = date_todo.strftime('%d-%m-%y')
            
        f.write(text_todo+'__'+str(date_todo)+'\n')
        f.close()
        return redirect(url_for('.admin_stuff'))
    
    elif 'modify' in idline:
        """ load txt in a list, add DONE --- to the idline list element and write new txt"""
        test = idline.split()[0]
        data1[int(test)]='DONE --- '+data1[int(test)]
        f = open('/home/pi/apiclock/admin.txt', 'w')
        for line in data1:
            f.write(line)
        f.close()
        return redirect(url_for('.admin_stuff'))
    
    elif 'delete' in idline:
        """ get the id (by splitting the line) of the element, delete it, re write the new txt"""
        test = idline.split()[0]
        del data1[int(test)]
        f = open('/home/pi/apiclock/admin.txt', 'w')
        for line in data1:
            f.write(line)
        f.close()
        return redirect(url_for('.admin_stuff'))
        
    return render_template('admin_stuff.html', form=form, data=data, today=today)