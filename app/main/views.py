# coding: utf-8
import subprocess
import os
import datetime

from flask import render_template, redirect, url_for, flash, request,\
                  current_app
from flask.ext.login import login_required, current_user
from flask.ext.mail import Mail, Message
from mpd import MPDClient
from threading import Thread

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, playerForm,\
                   addAdmin, ContactForm, snoozeForm
from .. import db
from ..email import send_email
from ..models import Role, User, Alarm, Music
from ..decorators import admin_required
from ..functions import jouerMPD, snooze, connectMPD

# ========================================
# ============ PAGES PUBLIQUES ===========
# ========================================


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('public/contact.html', form=form)
        else:
            msg = Message(form.subject.data,
                          sender='[Contact] - Apiclock',
                          recipients=['j_fiot@hotmail.com'])
            msg.body = """
            From: %s &lt; %s &gt; %s """ % (form.name.data,
                                            form.email.data,
                                            form.message.data)
            send_email(current_user.email,
                       'APICLOCK MAIL from '+form.email.data,
                       'auth/email/contact',
                       msg.body)
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
    """ List blog posts from file articles.txt """
    f = open(current_app.config['ADMIN_LIST'] + '/' +
             current_app.config['BLOG_POST'], 'r')
    data1 = f.readlines()
    data = [str(i)+'/'+val.decode('utf-8') for i, val in enumerate(data1)]

    return render_template('public/blog.html', articles=data)


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

# ========================================
# =========== PAGES SEMI PRIVEES =========
# ========================================


@main.route('/', methods=['GET', 'POST'])
def index():
    """ Connect MPD and check Play /stop"""
    connectMPD()
    client = MPDClient()
    if 'play' in request.form:
        client.add('http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3')
        client.play()
    elif 'stop' in request.form:
        client.stop()
        client.close()
    return render_template('index.html')

# ========================================
# ============= PAGES PRIVEES ============
# ========================================


@main.route('/dashboard', methods=['GET', 'POST'], defaults={'action': 4})
@main.route('/dashboard/<action>/<musique>', methods=['GET', 'POST'])
@login_required
@admin_required
def dashboard(action,
      musique="http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3"):

    """ Get and Print MPD state """
    if connectMPD():
        client = MPDClient()
        test = client.status()['state']
    else:
        test = False

    alarms = Alarm.query.filter_by(users=current_user.id).all()

    """ load todo list and search for today todo """
    f = open(current_app.config['ADMIN_LIST'] + '/' +
             current_app.config['TODO_LIST'], 'r')
    data1 = f.readlines()
    today = datetime.datetime.now().strftime('%d-%m-%y')
    listedujour = []
    for element in data1:
        if element[-9:-1] == today:
            """ Cut end (= date )and remove last element (/)
            then compare with date """
            element = element.decode('utf-8')
            listedujour.append(element[:-11])
        else:
            pass

    form1 = playerForm(prefix="form1")
    formsnooze = snoozeForm()

    if formsnooze.submitsnooze.data:
        """ Get radio by id and return url for jouerMPD()"""
        radiosnooze = formsnooze.radiosnooze.data
        radiosnooze = Music.query.filter(Music.id == radiosnooze).first()
        radiosnooze = radiosnooze.url
        minutessnooze = int(formsnooze.minutessnooze.data)
        snooze(radiosnooze, minutessnooze)
        return redirect(url_for('.dashboard'))

    elif form1.submit.data:
        """ Depending on media type get id and then request for url """

        if form1.radio.data != 0:
            mediaid = form1.radio.data
        elif form1.radio.data == 0:
            mediaid = form1.music.data
        else:
            mediaid = form1.music.data

        print form1.radio.data
        print form1.music.data
        print mediaid
        print form1.music.choices

        choosen_media = Music.query.filter(Music.id == mediaid).first()

        print type(choosen_media)
        return redirect(url_for('.dashboard'))

    # get in GET the action's param
    elif action == '1':
        """ Verify MPD connexion and play the urlmedia in args with volum """
        os.system('amixer sset PCM,0 94%')
        if connectMPD():
            client.stop()
            client.clear()
            client.add("http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3")
            client.play()
        else:
            flash('MPD not connected')
        return redirect(url_for('.dashboard'))

    elif action == '0':
        """ Verify MPD connection and stop and clear MPD playlist """
        if connectMPD():
            client.clear()
            client.stop()
            client.close()
        else:
            flash('MPD not connected')
        return redirect(url_for('.dashboard'))
    elif action == '2':
        """ Increase volume by 3dB """
        os.system('amixer sset PCM,0 3dB+')
        return redirect(url_for('.dashboard'))
    elif action == '3':
        """ Decrease volume by 3dB """
        os.system('amixer sset PCM,0 3dB-')
        return redirect(url_for('.dashboard'))
    else:
        return render_template('dashboard.html', form1=form1,
                               formsnooze=formsnooze, alarms=alarms,
                               listedujour=listedujour, test=test)


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
        user.email     = form.email.data
        user.username  = form.username.data
        user.confirmed = form.confirmed.data
        user.role      = Role.query.get(form.role.data)
        user.name      = form.name.data
        user.location  = form.location.data
        user.about_me  = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data     = user.email
    form.username.data  = user.username
    form.confirmed.data = user.confirmed
    form.role.data      = user.role_id
    form.name.data      = user.name
    form.location.data  = user.location
    form.about_me.data  = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    user = User.query.all()
    if request.args.get('id'):
        userid = request.args.get('id')
        userd = User.query.filter(User.id == userid).first()
        db.session.delete(userd)
        db.session.commit()
        flash('The user has been deleted.')
        return redirect(url_for('.users', users=user))
    return render_template('admin/users.html', users=user)


@main.route('/diskutil')
@login_required
@admin_required
def diskutil():
    commande = subprocess.Popen("df -h", stdout=subprocess.PIPE, shell=True)
    retour = commande.stdout.readlines()

    commande = subprocess.Popen("du -h ./app/static/musique",
                                stdout=subprocess.PIPE,
                                shell=True)
    retour2 = commande.stdout.readlines()

    return render_template('/admin/diskutil.html', test=retour, test2=retour2)


@main.route('/admin_stuff', methods=['GET', 'POST'])
@main.route('/admin_stuff/<idline>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_stuff(idline='0'):
    form = addAdmin()
    f = open(current_app.config['ADMIN_LIST'] + '/' +
             current_app.config['TODO_LIST'], 'r')
    data1 = f.readlines()
    data = [str(i) + '/' + val.decode('utf-8') for i, val in enumerate(data1)]
    today = datetime.datetime.now().strftime('%d-%m-%y')

    if form.validate_on_submit():
        f = open(current_app.config['ADMIN_LIST'] + '/' +
                 current_app.config['TODO_LIST'], 'a')
        """add line to the admin.txt with number and extract date """
        ajout = form.about_me.data
        """ Extract date if mentionned ('__') else add tomorow for the date"""
        if '__' in ajout:
            """ Slice string if date in todo """
            date_todo = ajout[-8:]
            date_todo = datetime.datetime.strptime(date_todo, '%d-%m-%y').date()
            text_todo = ajout[:-8]
        else:
            """ If no date in todo add due day to tomorow """
            text_todo = ajout
            date_todo = datetime.datetime.now() + datetime.timedelta(days=1)
            date_todo = date_todo.strftime('%d-%m-%y')

        f.write(u''.join(text_todo).encode('utf-8') + '__' +
                str(date_todo) + '\n')
        f.close()
        return redirect(url_for('.admin_stuff'))

    elif 'modify' in idline:
        """ Load txt in a list, add DONE --- to the idline list element
        and write new txt"""
        test = idline.split()[0]
        data1[int(test)] = 'DONE --- '+data1[int(test)]
        f = open(current_app.config['ADMIN_LIST'] + '/' +
                 current_app.config['TODO_LIST'], 'w')
        for line in data1:
            f.write(line)
        f.close()
        return redirect(url_for('.admin_stuff'))

    elif 'delete' in idline:
        """ Get the id (by splitting the line) of the element, delete it
        and re write the new txt """
        test = idline.split()[0]
        del data1[int(test)]
        f = open(current_app.config['ADMIN_LIST'] + '/' +
                 current_app.config['TODO_LIST'], 'wp')
        for line in data1:
            f.write(line)
        f.close()
        return redirect(url_for('.admin_stuff'))

    return render_template('admin_stuff.html', form=form,
                           data=data, today=today)
