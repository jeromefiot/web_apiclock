from flask import render_template, redirect, url_for, abort, flash, request
from flask.ext.login import login_required, current_user
from crontab import CronTab

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, addAlarmForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/admin_stuff')
def admin_stuff():
    return render_template('admin_stuff.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/alarm', methods=['GET', 'POST'])
@login_required
def alarm():
    form = addAlarmForm()
    jourscron = ''
    heurescron = ''
    minutescron = ''
    test = ''

    if form.validate_on_submit():
        recupjours = dict((key, request.form.getlist(key)) for key in request.form.keys())
        jourscron = ", ".join(recupjours['jours'])
        heurescron = form.heures.data
        minutescron = form.minutes.data
        
        # setting up crontab
        cron = CronTab()
        job = cron.new(command='/home/pi/apiclock/test_cron.py',
                       comment='alarme_radio' + ' : ' + current_user.username)
        job.dow.on(jourscron)
        job.hour.on(heurescron)
        job.minute.on(minutescron)
        job.enable()
        cron.write()
        
    return render_template("alarm.html", form=form, user=current_user, jours=jourscron, heures=heurescron,
                           minutes=minutescron)


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
