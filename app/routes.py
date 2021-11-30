from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/')
@app.route('/index')  # Отлавливание главной страницы
@login_required  # Функция защиты просмотра от незарегистрированнных пользователей
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])  # отлавливание страницы логина
def login():
    if current_user.is_authenticated:  # проверка пользователя на регистрацию
        return redirect(url_for('index'))  # перенаправление на главную
    form = LoginForm()  # создание формы логина
    if form.validate_on_submit():  # проверка на запрос POST
        user = User.query.filter_by(username=form.username.data).first()  # запрос пользователя из БД
        if user is None or not user.check_password(form.password.data):  # проверка пароля
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)  # регистрирование входа пользователя, если данные верны
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():  # проверка на запрос POST
        user = User(username=form.username.data, email=form.email.data)  # создание нового пользователя
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')  # username динамический компонент
@login_required  # только для зарегистрированных пользователей
def user(username):  # профиль пользователя
    user = User.query.filter_by(username=username).first_or_404()  # загрузка пользователя\выдача ошибки 404
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.before_request  # последняя активность пользователя
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():  # проверка на запрос POST
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()  # загрузка изменений пользователя в БД
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':  # помещаем данные из БД в формы(в случае запроса GET)
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
