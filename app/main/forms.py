from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, SelectMultipleField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, NumberRange
from wtforms import ValidationError
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import and_
from ..models import Role, User, Music

import feedparser


class playerForm(Form):
    radio = SelectField('Radio')
    podcast = SelectField('Podcast')
    music = SelectField('Music')
    submit = SubmitField('Jouer')

    def __init__(self, *args, **kwargs):
        super(playerForm, self).__init__(*args, **kwargs)
        self.radio.choices = [(g.id, g.name) for g in
            Music.query.filter(and_(Music.music_type=='1', Music.users==current_user.id)).all()]
        self.music.choices = [(g.id, g.name) for g in
            Music.query.filter(and_(Music.music_type=='3', Music.users==current_user.id)).all()]
        podcasts = Music.query.filter(and_(Music.music_type=='2', Music.users==current_user.id)).all()
        lemissions = []
        #recup pour chaque podcast les url de ts les emissions
        for emission in podcasts:
            d = feedparser.parse(emission.url)
            emissions=[(d.entries[i].enclosures[0]['href'],emission.name+' - '+d.entries[i]['title']) for i,j in enumerate(d.entries)]
            lemissions.extend(emissions)
        self.podcast.choices = lemissions
    
    
# faire un formulaire qui propose de jouer tous les medias
# impose un double menu deroulant (1 choix du type de media 2 populate le 2eme drop down )


class addAdmin(Form):
    """ add line to admin relinder list """
    about_me = TextAreaField('Ajouter')
    submit = SubmitField('valider')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')