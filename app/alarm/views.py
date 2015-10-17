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


@alarm.route('/', methods=['GET', 'POST'], defaults = {'action':'0', 'idr':'N'})
@alarm.route('/<action>/<idr>', methods=['GET', 'POST'])
@login_required
@admin_required
def index(action, idr):
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
        print jourscron
        return redirect(url_for('.index'))
        
    elif action == '1':
    # action = 1 = supprimer l'alarme de l'id passe en arg
        alarmedel = Alarm.query.filter(Alarm.id==idr).first()
        db.session.delete(alarmedel)
        removecron(idr)
        db.session.commit()
        flash('Alarm has been deleted')
        return redirect(url_for('.index'))
    
    elif action == '2':
    # retourne la page en edition avec l'alarme de l'id recu
        alarmeedit = Alarm.query.filter(Alarm.id==idr).first()
        print alarmeedit
        form = addAlarmForm(obj=alarmeedit)
    else:
        return render_template("alarm/alarm.html", form=form, user=current_user, alarms=alarms, radios=radios)