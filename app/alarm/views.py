from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from crontab import CronTab
import feedparser, datetime

from . import alarm
from .forms import addAlarmForm, addAlarmForm2
from .. import db
from ..models import Alarm, Music
from ..functions import addcronenvoi, removecron, statealarm
from ..decorators import admin_required

@alarm.route('/', methods=['GET', 'POST'], defaults={'action': '0', 'idr': 'N'})
@alarm.route('/<action>/<idr>', methods=['GET', 'POST'])
@login_required
@admin_required


def index(action, idr):
    alarms = Alarm.query.filter(Alarm.users == current_user.id).all()
    radios = Music.query.filter(and_(Music.music_type == '1',
        Music.users == current_user.id)).all()
<<<<<<< HEAD
    
    form  = addAlarmForm(state=True)
    form2 = addAlarmForm2(state=True)
=======
        
    form      = addAlarmForm(state=True)
    form2     = addAlarmForm2(state=True)
>>>>>>> f2bbad906243270e587ab60ca31f216bee349296
    monalarme = {}
    
    if form.validate_on_submit():
        monalarme['nom'] = form.name.data
        if form.state.data:
            monalarme['state'] = '1'
        else:
            monalarme['state'] = '0'
            
        # monalarme['duration'] = form.duration.data
        monalarme['heure']      = form.heures.data
        monalarme['minute']     = form.minutes.data
        monalarme['repetition'] = form.repetition.data
        monalarme['jours']      = form.jours.data
        monalarme['path']       = form.Radio.data.url
<<<<<<< HEAD
        
=======

>>>>>>> f2bbad906243270e587ab60ca31f216bee349296
        lastid = alarms[-1].id
        
        if lastid is None:
            monalarme['id'] = 1
        else:
            monalarme['id'] = lastid + 1
        
        #format data hour:minute in datetime python
        timepython = str(monalarme['heure'])+ ':' + str(monalarme['minute'])
        timepython = datetime.datetime.strptime(timepython, "%H:%M")
        
        ## setting up crontab
        result = addcronenvoi(monalarme)
        
        # Add alarm in database
        if result == 0:
            alarme = Alarm(
<<<<<<< HEAD
                    namealarme = monalarme['nom'],
                    state      = monalarme['state'],
                    #duration=timepython,
                    days=",".join([str(x) for x in monalarme['jours']]),
                    startdate=str(monalarme['heure'])
                         + ':' + str(monalarme['minute']),
                    frequence  = 'dows',
                    users      = current_user.id)
=======
                    namealarme  =monalarme['nom'],
                    state       =monalarme['state'],
                    # duration=monalarme['duration'],
                    days        =",".join([str(x) for x in monalarme['jours']]),
                    startdate   =str(monalarme['heure'])
                                + ':' + str(monalarme['minute']),
                    frequence   ='dows',
                    users       =current_user.id)
>>>>>>> f2bbad906243270e587ab60ca31f216bee349296
            db.session.add(alarme)
            try:
                db.session.commit()
                flash('Your alarm has been programed.'+monalarme['duration'])
            except:
                flash('Error adding your alarm in database.')
        else:
            flash('Error adding your alarm.')
        return redirect(url_for('.index'))

    # ******************************************************************
    # ******************************************************************

    elif form2.submit.data:
        monalarme['nom'] = form2.name.data
        if form2.state.data:
            monalarme['state']  = '1'
        else:
            monalarme['state']  = '0'
        # monalarme['duration'] = form.duration.data
        monalarme['heure']      = form2.heures.data
        monalarme['minute']     = form2.minutes.data
        monalarme['repetition'] = form2.repetition.data
        monalarme['jours']      = form2.jours.data
        monalarme['path']       = form2.radio.data
        
        flash (monalarme['path'])
        return redirect(url_for('.index'))
        # lastid = alarms[-1].id

        # if lastid is None:
            # monalarme['id'] = 1
        # else:
            # monalarme['id'] = lastid + 1
        
        # #format data hour:minute in datetime python
        # timepython = str(monalarme['heure'])+ ':' + str(monalarme['minute'])
        # timepython = datetime.datetime.strptime(timepython, "%H:%M")

        # ## setting up crontab
        # result = addcronenvoi(monalarme)

        # # Add alarm in database
        # if result == 0:
            # alarme = Alarm(
                    # namealarme=monalarme['nom'],
                    # state=monalarme['state'],
                    # #duration=timepython,
                    # days=",".join([str(x) for x in monalarme['jours']]),
                    # startdate=str(monalarme['heure'])
                         # + ':' + str(monalarme['minute']),
                    # frequence='dows',
                    # users=current_user.id)
            # db.session.add(alarme)
            # try:
                # db.session.commit()
                # flash('Your alarm has been programed.'+monalarme['duration'])
            # except:
                # flash('Error adding your alarm in database.')
        # else:
            # flash('Error adding your alarm.')
        # return redirect(url_for('.index'))

# ******************************************************************
# ******************************************************************
    
    elif action == '1':
<<<<<<< HEAD
    # action = 1 = remove alarm which id = idr
=======
    # action = 1 delete alarm by id (idr)
>>>>>>> f2bbad906243270e587ab60ca31f216bee349296
        alarmedel = Alarm.query.filter(Alarm.id == idr).first()
        db.session.delete(alarmedel)
        removecron(idr)
        db.session.commit()
        flash('Alarm has been deleted')
        return redirect(url_for('.index'))
    
    elif action == '2':
<<<<<<< HEAD
        # return alarm which id = idr in edition mode
        alarmeedit = Alarm.query.filter(Alarm.id == idr).first()
        form = addAlarmForm(obj=alarmeedit)
=======
    # edit alarm by id (idr)
        alarmeedit  = Alarm.query.filter(Alarm.id == idr).first()
        form        = addAlarmForm(obj=alarmeedit)
>>>>>>> f2bbad906243270e587ab60ca31f216bee349296
        return render_template("alarm/alarm.html",
             form=form, form2=form2, user=current_user, alarms=alarms, radios=radios)
    
    elif action == '3':
    # Call statealarm function which activate / deactivate alarm 
        statealarm(idr)
        return render_template("alarm/alarm.html",
            form=form, form2=form2, user=current_user, alarms=alarms, radios=radios)
    
    else:
        return render_template("alarm/alarm.html",
             form=form, form2=form2, user=current_user, alarms=alarms, radios=radios)