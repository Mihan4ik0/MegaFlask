from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


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


class EmptyForm(FlaskForm):  # пустая форма
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):  # форма редактирования постов
    post = TextAreaField('Напишите что-нибудь', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Опубликовать')
