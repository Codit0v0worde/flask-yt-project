from flask import Blueprint, redirect, render_template, flash, request, url_for
from flask_login import login_user , logout_user

from ..functions import save_picture
from ..forms import RegistrationForm , LoginForm
from ..extensions import db , bcrypt
from ..models.user import User

user=Blueprint('user', __name__)

@user.route('/user/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        user = User(name=form.name.data, login=form.login.data, avatar=avatar_filename, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Отличная работа, {form.login.data}! Вы смогли зарегистрироваться!", "success")
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        flash("При регистрации произошла ошибка. Проверьте введённые данные.", "danger")
        print(form.errors)
    return render_template('user/register.html', form=form)


@user.route('/user/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Добро пожаловать, {user.name}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('post.all_posts'))
        else:
            flash("Ошибка входа. Протрите глаза и проверьте логин и пароль!", "danger")
    return render_template('user/login.html', form=form)


@user.route('/user/logout' , methods=['POST', 'GET'] )
def logout():
    logout_user()
    return redirect(url_for('post.all_posts'))
    