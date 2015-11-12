from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Music


class AddMusicForm(Form):
<<<<<<< HEAD
    music_type = SelectField('Type', choices=[('1','Radio'),('2','Podcast'),('3','Musique')])
    name = StringField('Nom', validators=[Length(1, 64)])
    url = StringField('Url', validators=[Length(1, 128)])
    description = TextAreaField('Description')
    submit = SubmitField('Ajouter')
=======
    name        = StringField('Nom', validators=[Length(1, 64)])
    url         = StringField('Url', validators=[Length(1, 128)])
    description = TextAreaField('Description')
    music_type  = SelectField('Type', choices=[('1','Radio'),('2','Podcast'),('3','Musique')])
    submit      = SubmitField('Ajouter')
>>>>>>> f2bbad906243270e587ab60ca31f216bee349296

    
class PlayRadio(Form):
    submit      = SubmitField('Play')
    submit2     = SubmitField('Stop')
