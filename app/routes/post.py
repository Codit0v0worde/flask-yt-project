from flask import Blueprint, abort, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from ..extensions import db
from ..models.post import Post
from ..forms import StudentForm, TeacherForm  
from ..models.user import User

post = Blueprint('post', __name__)

@post.route('/')
def index():
    return redirect(url_for('post.all_posts'))

@post.route('/all', methods=['GET', 'POST'])
def all_posts():
    form = TeacherForm()
    teachers = User.query.filter_by(status='teacher').all()
    form.teacher.choices = [(0, 'Все преподаватели')] + [(t.id, t.name) for t in teachers]

    if form.validate_on_submit():  
        teacher_id = form.teacher.data
        if teacher_id == 0:
            posts = Post.query.order_by(Post.date.desc()).all()
        else:
            posts = Post.query.filter_by(teacher=teacher_id).order_by(Post.date.desc()).all()
    else:
        posts = Post.query.order_by(Post.date.desc()).limit(20).all()

    return render_template('post/all.html', posts=posts, user=User, form=form)

@post.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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

    if post.teacher != current_user.id:
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

    if post.teacher != current_user.id:
        abort(403)  
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Тема успешно удалена!', 'success')
    except Exception as e:
        print(str(e))
        flash('Ошибка при удалении темы', 'danger')

    return redirect(url_for('post.all_posts'))