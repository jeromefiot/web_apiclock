from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from crontab import CronTab
import feedparser

from . import alarm
from .forms import addAlarmForm
from .. import db
from ..models import Role, User, Alarm, Music
from ..functions import addcronenvoi, removecron
from ..decorators import admin_required


@alarm.route('/', methods=['GET', 'POST'],
     defaults={'action': '0', 'idr': 'N'})
@alarm.route('/<action>/<idr>', methods=['GET', 'POST'])
@login_required
@admin_required
def index(action, idr):
    alarms = Alarm.query.filter(Alarm.users == current_user.id).all()
    radios = Music.query.filter(and_(Music.music_type == '1',
        Music.users == current_user.id)).all()
    form = addAlarmForm()
    monalarme = {}

    if form.validate_on_submit():
        monalarme['nom'] = form.name.data
        monalarme['heure'] = form.heures.data
        monalarme['minute'] = form.minutes.data
        monalarme['repetition'] = form.repetition.data
        monalarme['jours'] = form.jours.data
        monalarme['path'] = form.Radio.data.url

        lastid = alarms[-1].id

        if lastid is None:
            monalarme['id'] = 1
        else:
            monalarme['id'] = lastid + 1

        ## setting up crontab
        result = addcronenvoi(monalarme)
        if result == 0:
            alarme = Alarm(
                    namealarme=monalarme['nom'],
                    days=",".join([str(x) for x in monalarme['jours']]),
                    startdate=str(monalarme['heure'])
                         + ':' + str(monalarme['minute']),
                    frequence='dows',
                    users=current_user.id)
            db.session.add(alarme)
            try:
                db.session.commit()
                flash('Your alarm has been programed.')
            except:
                flash('Error adding your alarm in database.')
        else:
            flash('Error adding your alarm.')
        return redirect(url_for('.index'))

    elif action == '1':
    # action = 1 = supprimer l'alarme de l'id passe en arg
        alarmedel = Alarm.query.filter(Alarm.id == idr).first()
        db.session.delete(alarmedel)
        removecron(idr)
        db.session.commit()
        flash('Alarm has been deleted')
        return redirect(url_for('.index'))

    elif action == '2':
    # retourne la page en edition avec l'alarme de l'id recu
        alarmeedit = Alarm.query.filter(Alarm.id == idr).first()
        print alarmeedit
        form = addAlarmForm(obj=alarmeedit)
        return render_template("alarm/alarm.html",
             form=form, user=current_user, alarms=alarms, radios=radios)
    else:
        return render_template("alarm/alarm.html",
             form=form, user=current_user, alarms=alarms, radios=radios)