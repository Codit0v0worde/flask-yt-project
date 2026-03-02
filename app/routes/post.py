from flask import Blueprint, abort, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from ..functions import save_comment_file
from ..extensions import db
from ..models.post import Post
from ..forms import StudentForm, TeacherForm  
from ..models.user import User
from ..forms import CommentForm
from ..models.comment import Comment

post = Blueprint('post', __name__)

@post.route('/')
def index():
    return redirect(url_for('post.all_posts'))

@post.route('/all', methods=['GET', 'POST'])
def all_posts():
    form = TeacherForm()
    teachers = User.query.filter_by(status='teacher').all()
    form.teacher.choices = [(0, 'Все преподаватели')] + [(t.id, t.name) for t in teachers]

    # Получаем поисковый запрос из GET-параметра
    search_query = request.args.get('q', '').strip()

    if form.validate_on_submit():
        # Если отправлена форма фильтрации (POST)
        teacher_id = form.teacher.data
        # Перенаправляем на GET, сохраняя параметры
        return redirect(url_for('post.all_posts', teacher=teacher_id, q=search_query))
    else:
        # При GET-запросе берём параметры из URL
        teacher_id = request.args.get('teacher', type=int, default=0)

    # Формируем запрос к базе
    query = Post.query

    # Фильтр по преподавателю
    if teacher_id and teacher_id != 0:
        query = query.filter_by(teacher=teacher_id)

    # Поиск по названию темы (регистронезависимо)
    if search_query:
        query = query.filter(Post.subject.ilike(f'%{search_query}%'))

    # Сортировка по дате (сначала новые)
    query = query.order_by(Post.date.desc())

    # Если нет ни фильтра, ни поиска, показываем последние 20
    if not teacher_id and not search_query:
        posts = query.limit(20).all()
    else:
        posts = query.all()

    return render_template('post/all.html', posts=posts, form=form, search_query=search_query)

@post.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.status not in ['teacher', 'enginiger']:
        abort(403)   
    form = StudentForm()
    form.student.choices = [(u.id, u.name) for u in User.query.filter_by(status='user').all()]
    
    if form.validate_on_submit():
        subject = form.subject.data
        student_id = form.student.data  
        new_post = Post(teacher=current_user.id, subject=subject, student=student_id)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('post.all_posts'))
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    return render_template('post/create.html', form=form)

@post.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if not post:
        return redirect(url_for('post.all_posts'))

    # Разрешить, если пользователь – автор ИЛИ суперпользователь
    if post.teacher != current_user.id and current_user.status != 'enginiger':
        abort(403)

    form = StudentForm()
    form.student.choices = [(u.id, u.name) for u in User.query.filter_by(status='user').all()]

    if form.validate_on_submit():
        post.subject = form.subject.data
        post.student = form.student.data
        try:
            db.session.commit()
            flash('Тема успешно обновлена!', 'success')
            return redirect(url_for('post.all_posts'))
        except Exception as e:
            print(str(e))
            flash('Ошибка при обновлении темы', 'danger')
    else:
        form.subject.data = post.subject
        form.student.data = post.student

    return render_template('post/update.html', post=post, form=form)

@post.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get(id)
    if not post:
        abort(404)

    if post.teacher != current_user.id and current_user.status != 'enginiger':
        abort(403)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Тема успешно удалена!', 'success')
    except Exception as e:
        print(str(e))
        flash('Ошибка при удалении темы', 'danger')

    return redirect(url_for('post.all_posts'))

@post.route('/post/<int:id>', methods=['GET'])
def post_detail(id):
    post = Post.query.get_or_404(id)
    comments = post.comments.filter(Comment.parent_id == None).order_by(Comment.created_at.desc()).all()
    form = CommentForm()
    return render_template('post/detail.html', post=post, comments=comments, form=form)

@post.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        filename = None
        if form.file.data:
            filename = save_comment_file(form.file.data)
        
        comment = Comment(
            content=form.content.data,
            file_path=filename,
            user_id=current_user.id,
            post_id=post.id,
            parent_id=form.parent_id.data or None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
    else:
        flash('Ошибка при добавлении комментария', 'danger')
        print(form.errors)
    
    return redirect(url_for('post.post_detail', id=post.id))