from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class RegistrationForm(FlaskForm):  # создание формы регистрации пользователя
    username = StringField('Имя пользователя', validators=[DataRequired()])  # форма с проверкой на наполненность
    email = StringField('Электронная почта', validators=[DataRequired(),
                                                         Email()])  # форма с проверкой на наполненность и соответствие структуре email
    password = PasswordField('Пароль', validators=[DataRequired()])  # форма с проверкой на наполненность
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo(
        'password')])  # форма с проверкой на наполненность и соответствием полю 'password'
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):  # проверка имени на уникальность
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другое имя')

    def validate_email(self, email):  # проверка почты на уникальность
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другую электронную почту')


class LoginForm(FlaskForm):  # создание формы входа пользователя
    username = StringField('Имя пользователя', validators=[DataRequired()])  # форма с проверкой на наполненность
    password = PasswordField('Пароль', validators=[DataRequired()])  # форма с проверкой на наполненность
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ResetPasswordRequestForm(FlaskForm):  # форма запроса на сброс пароля
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Запросить Сброс Пароля')


class ResetPasswordForm(FlaskForm):  # форма сброса пароля
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сменить пароль')
