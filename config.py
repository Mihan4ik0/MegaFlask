import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-KNOW'  # криптографический ключ
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')  # местоположение БД
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # отслеживание изменений БД
