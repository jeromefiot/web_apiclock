from flask.ext.wtf import Form
from wtforms import SubmitField, SelectMultipleField, IntegerField, SelectField, StringField
from wtforms.validators import Required, NumberRange, Length
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Role, User, Alarm, Music, getradios


class addAlarmForm(Form):
    name = StringField('Nom', validators=[Length(1, 120)])
    #renvoi une query pour un selectfield : http://stackoverflow.com/questions/26254971/more-specific-sql-query-with-flask-wtf-queryselectfield
    Radio = QuerySelectField('Radios', query_factory=getradios, get_label='name')
    
    jours = SelectMultipleField('jours', choices=[('1','Lundi'),('2','Mardi'),('3','Mercredi'),('4','Jeudi'),('5','Vendredi')
        ,('6','Samedi'),('0','Dimanche')], validators=[Required()])
    heures = IntegerField('Heures', validators=[NumberRange(min=0, max=23)])
    minutes = IntegerField('Minutes', validators=[NumberRange(min=0, max=59)])
    #duration = StringField('Duration in Minutes', validators=[Length(5, 5)])
    frequence = SelectField('Frequence', choices=[('0','One shot'),
                                                ('days','Jours'),
                                                ('dows','Semaine'),
                                                ('frequency_per_year','An'),
                                                ('reboot','Reboot')])
    submit = SubmitField('valider')