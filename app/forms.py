from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):  # создание формы входа пользователя
    username = StringField('Имя пользователя', validators=[DataRequired()])  # форма с проверкой на наполненность
    password = PasswordField('Пароль', validators=[DataRequired()])  # форма с проверкой на наполненность
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):  # создание формы регистрации пользователя
    username = StringField('Имя пользователя', validators=[DataRequired()])  # форма с проверкой на наполненность
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])  # форма с проверкой на наполненность и соответствие структуре email
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


class EditProfileForm(FlaskForm):  # форма редактирования профиля
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Опубликовать')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста введите другое имя пользователя')


class PostForm(FlaskForm):  # форма для ввода нового сообщения
    post = TextAreaField('Напишите что-нибудь', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Опубликовать')


class ResetPasswordRequestForm(FlaskForm):  # форма запроса на сброс пароля
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Запросить Сброс Пароля')


class ResetPasswordForm(FlaskForm):  # форма сброса пароля
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сменить пароль')
