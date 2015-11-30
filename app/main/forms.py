from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, TextField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.login import current_user
from sqlalchemy.sql import and_

from ..models import Role, User, Music


class snoozeForm(Form):

    """Snooze adding form."""

    radiosnooze = SelectField('Radio')
    minutessnooze = SelectField('Duree')
    submitsnooze = SubmitField("Snooze")

    def __init__(self, *args, **kwargs):

        """Query for form list value."""

        super(snoozeForm, self).__init__(*args, **kwargs)
        """Define choice for radio field / important = id must be string"""
        self.radiosnooze.choices = [(str(g.id), g.name) for g in
                    Music.query.filter(and_(Music.music_type == '1',
                    Music.users == current_user.id)).all()]
        """Define a list from 0 to 60."""
        dureesnooze = list(range(1, 60))
        self.minutessnooze.choices = [(str(g), str(g)) for g in dureesnooze]


class ContactForm(Form):

    """Contact form with mail."""

    name = TextField("Name", validators=[Required("Please enter your name.")])
    email = TextField("Email",
                      validators=[Required("Please enter your email address."),
                                  Email("Please enter your email address.")])
    subject = TextField("Subject",
                        validators=[Required("Please enter a subject.")])
    message = TextAreaField("Message",
                            validators=[Required("Please enter a message.")])
    submit = SubmitField("Send")


class playerForm(Form):

    """Play media on dashboard."""

    # media = SelectField('', choices=[('1', 'Radio'), ('2', 'Podcast'),
    #                        ('3', 'Musique')])
    media = SelectField('', choices=[('1', 'Radio'), ('3', 'Musique')])
    radio = SelectField('')
    # podcast = SelectField('')
    music = SelectField('')
    submit = SubmitField('Jouer')

    def __init__(self, *args, **kwargs):
        """Query for form list values."""

        super(playerForm, self).__init__(*args, **kwargs)
        self.radio.choices = [(g.id, g.name) for g in
                              Music.query.filter(and_(Music.music_type == '1',
                              Music.users == current_user.id)).all()]
        self.radio.choices.append((0, 'Choose Radio'))

        self.music.choices = [(g.id, g.name) for g in
                              Music.query.filter(and_(Music.music_type == '3',
                              Music.users == current_user.id)).all()]
        self.music.choices.append((0, 'Choose Media'))
        # podcasts = Music.query.filter(and_(Music.music_type=='2',
        #            Music.users==current_user.id)).all()
        # lemissions = []
        # get all url for emissions of a podcast
        #
        # for emission in podcasts:
        #    d = feedparser.parse(emission.url)
        #    emissions=[(d.entries[i].enclosures[0]['href'],
        #                emission.name + ' - ' + d.entries[i]['title'])\
        #                for i, j in enumerate(d.entries)]
        #    lemissions.extend(emissions)
        # self.podcast.choices = lemissions


class addAdmin(Form):

    """Add line to admin relinder list."""

    about_me = TextAreaField('Ajouter')
    submit = SubmitField('valider')


class EditProfileForm(Form):

    """Edit user profile."""

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):

    """Edit admin user form."""

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
        """Query role for list form values."""
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """Validate mail."""
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """Validate unique username."""
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
