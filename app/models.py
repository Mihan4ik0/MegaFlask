from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login
from hashlib import md5


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
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'  # backref определяет доступность с правой стороны, lazy определяет режим выполнения запроса
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):  # хэширование пароля
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):  # проверка пароля
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):  # изображение аватара
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()   # конвертирование почты в нижний регистр, далее в 16-ю строку
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
        return followed.union(own).order_by(Post.timestamp.desc())  # объединение 'followed' и 'own', а после сортировка по времени публикации


class Post(db.Model):  # таблица постов в БД
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader  # регистрирование пользовательского загрузчика
def load_user(id):
    return User.query.get(int(id))
