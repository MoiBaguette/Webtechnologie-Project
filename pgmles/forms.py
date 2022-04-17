from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20) ])
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[ DataRequired() ])
    confirm_password = PasswordField('Wachtwoord herhalen', validators=[ DataRequired(), EqualTo('password') ])
    submit = SubmitField('Registeren')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Deze gebruikersnaam bestaat al, kies een andere.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Deze e-mail bestaat al, log in als dat uw e-mail is')


class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[ DataRequired() ])
    remember = BooleanField('Herinneren')
    submit = SubmitField('Inloggen')


class UpdateAccountForm(FlaskForm):
    username = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20) ])
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    picture = FileField('Profielfoto bewerken', validators=[ FileAllowed(['jpg', 'png']) ])
    submit = SubmitField('Bewerken')

    def validate_username(self, username):
        if username.data != current_user.username and User.query.filter_by(username=username.data).first():
            raise ValidationError('Deze gebruikersnaam bestaat al, kies een andere.')

    def validate_email(self, email):
        if email.data != current_user.email and User.query.filter_by(email=email.data).first():
            raise ValidationError('Deze e-mail bestaat al, log in als dat uw e-mail is')

class NewCourseForm(FlaskForm):
    name = StringField('Naam', validators=[ DataRequired(), Length(min=1, max=100) ])
    description = TextAreaField('Beschrijving', validators=[ DataRequired() ])
    teacher_id = SelectField('Docent', validators=[ DataRequired() ], coerce=int)
    weekday = SelectField('Weekdag', choices=list(enumerate([ 'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag' ])))
    start = StringField('Begin', validators=[ DataRequired() ])
    end = StringField('Einde', validators=[ DataRequired() ])
    location = StringField('Locatie', validators=[ DataRequired(), Length(min=1, max=100) ])
    submit = SubmitField('Versturen')


class SubscribeForm(FlaskForm):
    lang_id = HiddenField()
    submit = SubmitField('Inschrijven')


class UnsubscribeForm(FlaskForm):
    lang_id = HiddenField()
    submit = SubmitField('Uitschrijven')

class SearchForm(FlaskForm):
    username = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Zoeken')

class AdminForm(FlaskForm):
    type = SelectField('Type',  choices=[('client', 'Klant'), ('teacher', 'Docent'), ('admin', 'Administrator')])
    submit = SubmitField('Bewerken')
