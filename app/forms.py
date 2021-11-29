from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):  # создание формы входа входа пользователя
    username = StringField('Username', validators=[DataRequired()])  # форма с проверкой на наполненность
    password = PasswordField('Password', validators=[DataRequired()])  # форма с проверкой на наполненность
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])  # форма с проверкой на наполненность
    email = StringField('Email', validators=[DataRequired(), Email()])  # форма с проверкой на наполненность и соответствие структуре email
    password = PasswordField('Password', validators=[DataRequired()])  # форма с проверкой на наполненность
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo(
        'password')])  # форма с проверкой на наполненность и соответствием полю 'password'
    submit = SubmitField('Register')

    def validate_username(self, username):  # проверка имени на уникальность
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):  # проверка почты на уникальность
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
