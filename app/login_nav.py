from flask.ext.wtf import Form
from flask.ext.login import login_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email
from flask import redirect, url_for, flash
from .models import User


class LoginFormNav(Form):

    """Form login for bootstrap nav."""

    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def validateFormNav(self):
        """Validate login form in nav."""
        if self.validate_on_submit():
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None and user.verify_password(self.password.data):
                login_user(user, self.remember_me.data)
                return redirect(url_for('main.dashboard'))
            flash('Invalid username or password.')
