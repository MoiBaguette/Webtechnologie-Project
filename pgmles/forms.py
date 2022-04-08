from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (BooleanField, HiddenField, PasswordField, StringField,
                     SubmitField, TextAreaField, SelectField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from .models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')


class LanguageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    info = TextAreaField('Info', validators=[DataRequired()])
    submit = SubmitField('Update')

class NewCourseForm(FlaskForm):
    name = StringField('Title', validators=[
                           DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    teacher_id = SelectField('Teacher', validators=[DataRequired()], coerce=int)
    weekday = StringField('Weekday', validators=[DataRequired()])
    start = StringField('Start', validators=[DataRequired()])
    end = StringField('End', validators=[DataRequired()])
    location = StringField('Location', validators=[
                           DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add')


class SubscribeForm(FlaskForm):
    lang_id = HiddenField()
    submit = SubmitField('Subscribe')


class UnsubscribeForm(FlaskForm):
    lang_id = HiddenField()
    submit = SubmitField('Unsubscribe')


class PostForm(FlaskForm):  # redundant
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
