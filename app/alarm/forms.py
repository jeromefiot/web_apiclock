from flask.ext.wtf import Form
from wtforms import SubmitField, SelectMultipleField, IntegerField, \
    SelectField, StringField, RadioField, BooleanField
from wtforms.validators import Required, NumberRange, Length
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Role, User, Alarm, Music, getradios


class addAlarmForm(Form):
    name = StringField('Nom', validators=[Length(1, 120)])
    state = BooleanField('Active')
    # duration = SelectField('Duree', choices=[('5', '5 mn'), ('10', '10 mn'),
        # ('15', '15 mn'), ('20', '20 mn'), ('30', '30 mn'), ('45', '45 mn'), ('59', '1 h')])
    Radio = QuerySelectField('Radios',
         query_factory=getradios, get_label='name')
    heures = IntegerField('Heures', validators=[NumberRange(min=0, max=23)])
    minutes = IntegerField('Minutes', validators=[NumberRange(min=0, max=59)])
    repetition = RadioField('List', choices=[('Repeter ? ',
    'Repeter l\'alarme')])
    jours = SelectMultipleField('jours', choices=[('1', 'Lundi'),
        ('2', 'Mardi'), ('3', 'Mercredi'), ('4', 'Jeudi'), ('5', 'Vendredi'),
        ('6', 'Samedi'), ('0', 'Dimanche')], validators=[Required()])
    submit = SubmitField('valider')