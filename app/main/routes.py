from app import db
from flask import render_template, flash, redirect, url_for, request, current_app
from app.main.forms import EditProfileForm, PostForm, EmptyForm, EditPostForm
from app.models import User, Post
from flask_login import current_user, login_required
from datetime import datetime
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])  # Отлавливание главной страницы
@login_required  # Функция защиты просмотра от незарегистрированнных пользователей
def index():  # логика главной страницы
    form = PostForm()  # создание формы публикации постов
    if form.validate_on_submit():  # проверка формы на пустоту и загрузка в БД
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост опубликован')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)  # нумерация страниц
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'],
                                                   False)  # отображение постов только от отслеживаемых
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home Page', form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')  # username динамический компонент
@login_required  # только для зарегистрированных пользователей
def user(username):  # логика страницы пользователя
    user = User.query.filter_by(username=username).first_or_404()  # загрузка пользователя\выдача ошибки 404
    page = request.args.get('page', 1, type=int)  # логика страниц
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(  # отображение постов
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.before_request  # последняя активность пользователя
def before_request():  # логика последней активности пользователя
    if current_user.is_authenticated:  # проверка на авторизацию
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():  # логика страницы изменения профиля
    form = EditProfileForm(current_user.username)  # форма изменения профиля
    if form.validate_on_submit():  # проверка на запрос POST
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()  # загрузка изменений пользователя в БД
        flash('Ваши изменения были сохранены')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':  # помещаем данные из БД в формы(в случае запроса GET)
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):  # логика подписки
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Пользователь {} не найден .'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('Вы не можете подписаться на самого себя!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('Вы подписались на  {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):  # логика подписки
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Пользователь {} не найден.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('Вы не можете отписаться от самого себя')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('Вы отписались от  {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():  # логика страницы с постами от всех пользователей
    page = request.args.get('page', 1, type=int)  # логика нумерации страниц
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'],
                                                                False)  # логика отображение постов
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/post/<id>')
@login_required
def post(id):  # отображение поста
    post = Post.query.filter_by(id=id).first_or_404()  # загрузка пользователя\выдача ошибки 404
    return render_template('post.html', post=post, id=id)


@bp.route('/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):  # редактирование постов
    form = EditPostForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        post.body = form.post.data
        db.session.commit()
        flash('Ваши изменения сохранены.')
        return redirect(url_for('main.explore'))
    elif request.method == 'GET':
        form.post.data = post
    return render_template('edit_post.html', title='Edit Post',
                           form=form)


@bp.route('/delete_post/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):  # удаление постов
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('main.explore'))
