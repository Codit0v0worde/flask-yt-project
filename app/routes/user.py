from flask import Blueprint, abort, redirect, render_template, flash, request, url_for
from flask_login import current_user, login_required, login_user , logout_user
from ..forms import ProfileForm
from ..functions import save_picture
from ..forms import RegistrationForm , LoginForm
from ..extensions import db , bcrypt
from ..models.user import User
from ..forms import ManageUserForm
from ..models.comment import Comment

user = Blueprint('user', __name__)

@user.route('/user/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        user = User(name=form.name.data, login=form.login.data, avatar=avatar_filename, password=hashed_password)

        # Назначаем роль: первый пользователь — enginiger, остальные — user
        if User.query.count() == 0:
            user.status = 'enginiger'
        else:
            user.status = 'user'

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

@user.route('/user/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('post.all_posts'))

@user.route('/manage-users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Разрешаем starosta и enginiger
    if current_user.status not in ['starosta', 'enginiger']:
        abort(403)

    form = ManageUserForm()

    if request.method == 'POST':
        print("=== POST-запрос к /manage-users ===")
        print("request.form:", dict(request.form))
        print("form.csrf_token:", form.csrf_token.data if form.csrf_token else "None")

    if form.validate_on_submit():
        print(" Форма валидна")
        user_id = form.user_id.data
        new_status = form.status.data
        print(f"  user_id = {user_id} (тип: {type(user_id)})")
        print(f"  status = {new_status}")

        target_user = User.query.get(user_id)
        if target_user:
            if target_user.id == current_user.id:
                flash('Вы не можете изменить свой собственный статус', 'danger')
            else:
                target_user.status = new_status
                try:
                    db.session.commit()
                    flash(f'Статус пользователя {target_user.login} изменён на {new_status}', 'success')
                    print(f"   Статус изменён на {new_status}")
                except Exception as e:
                    db.session.rollback()
                    flash('Ошибка при сохранении в БД', 'danger')
                    print(f"   Ошибка commit: {e}")
        else:
            print(f"   Пользователь с id {user_id} не найден")
            flash('Пользователь не найден', 'danger')

        return redirect(url_for('user.manage_users'))
    else:
        if request.method == 'POST':
            print(" Форма не валидна. Ошибки:", form.errors)
            flash('Ошибка валидации формы. Проверьте введённые данные.', 'danger')
        else:
            print("GET-запрос к /manage-users")

    users = User.query.filter(User.id != current_user.id).all()
    return render_template('user/manage_users.html', users=users, form=form)

@user.route('/profile', methods=['GET'])
@login_required
def profile():
    comments = current_user.comments.order_by(Comment.created_at.desc()).all()
    return render_template('user/profile.html', user=current_user, comments=comments)

@user.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Обновляем имя
        current_user.name = form.name.data
        
        # Обработка нового аватара
        if form.avatar.data:
            avatar_filename = save_picture(form.avatar.data)
            current_user.avatar = avatar_filename
        
        # Смена пароля (если заполнен старый и новый)
        if form.old_password.data and form.new_password.data:
            if bcrypt.check_password_hash(current_user.password, form.old_password.data):
                current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            else:
                flash('Неверный старый пароль', 'danger')
                return redirect(url_for('user.profile_edit'))
        
        try:
            db.session.commit()
            flash('Профиль успешно обновлён', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении', 'danger')
            print(str(e))
    
    # GET-запрос: предзаполняем имя
    form.name.data = current_user.name
    return render_template('user/profile_edit.html', form=form)