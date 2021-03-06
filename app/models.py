from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app

followers = db.Table('followers',  # Вспомогательная таблица
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):  # таблица пользователей в БД
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,  # secondary - таблица конфигураций
        primaryjoin=(followers.c.follower_id == id),  # условие связывающее с левой стороны(follower)
        secondaryjoin=(followers.c.followed_id == id),  # условие связывающее с правой стороны(followed)
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
        # backref определяет доступность с правой стороны, lazy определяет режим выполнения запроса
    )

    def __repr__(self):
        return '<Пользователь {}>'.format(self.username)

    def set_password(self, password):  # хэширование пароля
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):  # проверка пароля
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):  # изображение аватара
        digest = md5(self.email.lower().encode(
            'utf-8')).hexdigest()  # конвертирование почты в нижний регистр, далее в 16-ю строку
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):  # метод подписки
        if not self.is_following(user):  # проверка на отсутствие подписки
            self.followed.append(user)  # подписка на пользователя

    def unfollow(self, user):  # метод отписки
        if self.is_following(user):  # проверка на наличие подписка
            self.followed.remove(user)  # удаление подписки

    def is_following(self, user):  # метод проверки на наличие подписки
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):  # единый запрос БД
        followed = Post.query.join(  # объединение в таблицу ассоциаций подписчиков
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)  # фильтрация, чтобы вывести только тех за кем следит пользователь
        own = Post.query.filter_by(user_id=self.id)  # вывод своих постов
        return followed.union(own).order_by(
            Post.timestamp.desc())  # объединение 'followed' и 'own', а после сортировка по времени публикации

    def get_reset_password_token(self, expires_in=600):  # генерация токена
        return jwt.encode(
            {'reset password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')  # токен в строку

    @staticmethod  # обозначение статическим методом
    def verify_reset_password_token(token):  # функция декодирование токена
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):  # таблица постов в БД
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '{}'.format(self.body)


@login.user_loader  # регистрирование пользовательского загрузчика
def load_user(id):
    return User.query.get(int(id))
