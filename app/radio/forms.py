from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import Length


class AddMusicForm(Form):

    """Adding music Form."""

    name = StringField('Nom', validators=[Length(1, 64)])
    url = StringField('Url', validators=[Length(1, 128)])
    description = TextAreaField('Description')
    music_type = SelectField('Type', choices=[('1', 'Radio'), ('2', 'Podcast'),
                                              ('3', 'Musique')])
    submit = SubmitField('Ajouter')


class PlayRadio(Form):

    """Control music form button."""

    submit = SubmitField('Play')
    submit2 = SubmitField('Stop')
