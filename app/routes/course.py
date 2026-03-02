from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from datetime import datetime
from ..extensions import db
from ..models.user import User
from ..models.course import Course
from ..models.section import Section
from ..models.activity import Activity
from ..models.submission import Submission
from ..forms import CourseForm, SectionForm, ActivityForm, SubmissionForm, GradeForm
from ..functions import save_activity_file, save_submission_file
import pytz
import traceback

course = Blueprint('course', __name__)

# Часовой пояс Москвы
moscow_tz = pytz.timezone('Europe/Moscow')
utc_tz = pytz.utc

def moscow_to_utc(dt):
    if dt is None:
        return None
    moscow_dt = moscow_tz.localize(dt)
    utc_dt = moscow_dt.astimezone(utc_tz)
    return utc_dt.replace(tzinfo=None)

def utc_to_moscow(dt):
    if dt is None:
        return None
    utc_dt = utc_tz.localize(dt)
    moscow_dt = utc_dt.astimezone(moscow_tz)
    return moscow_dt.replace(tzinfo=None)

# Список курсов
@course.route('/courses')
def list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('course/list.html', courses=courses)

# Детальная страница курса
@course.route('/course/<int:id>')
def view_course(id):
    course = Course.query.get_or_404(id)
    sections = course.sections.order_by(Section.position).all()
    return render_template('course/view.html', course=course, sections=sections)

# Создание курса
@course.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.status not in ['teacher', 'enginiger']:
        abort(403)
    form = CourseForm()
    print("request.files =", request.files)
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Курс создан', 'success')
        return redirect(url_for('course.view_course', id=course.id))
    return render_template('course/form.html', form=form, title='Создание курса')

# Редактирование курса
@course.route('/course/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    if course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        db.session.commit()
        flash('Курс обновлён', 'success')
        return redirect(url_for('course.view_course', id=course.id))
    return render_template('course/form.html', form=form, title='Редактирование курса')

# Удаление курса
@course.route('/course/<int:id>/delete', methods=['POST'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    if course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    db.session.delete(course)
    db.session.commit()
    flash('Курс удалён', 'success')
    return redirect(url_for('course.list_courses'))

# Создание раздела
@course.route('/course/<int:course_id>/section/create', methods=['GET', 'POST'])
@login_required
def create_section(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = SectionForm()
    if form.validate_on_submit():
        max_pos = db.session.query(db.func.max(Section.position)).filter_by(course_id=course.id).scalar() or -1
        section = Section(
            title=form.title.data,
            description=form.description.data,
            position=max_pos + 1,
            course_id=course.id
        )
        db.session.add(section)
        db.session.commit()
        flash('Раздел создан', 'success')
        return redirect(url_for('course.view_course', id=course.id))
    return render_template('course/section_form.html', form=form, course=course, title='Новый раздел')

# Редактирование раздела
@course.route('/section/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_section(id):
    section = Section.query.get_or_404(id)
    if section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = SectionForm(obj=section)
    if form.validate_on_submit():
        section.title = form.title.data
        section.description = form.description.data
        db.session.commit()
        flash('Раздел обновлён', 'success')
        return redirect(url_for('course.view_course', id=section.course.id))
    return render_template('course/section_form.html', form=form, course=section.course, title='Редактирование раздела')

# Удаление раздела
@course.route('/section/<int:id>/delete', methods=['POST'])
@login_required
def delete_section(id):
    section = Section.query.get_or_404(id)
    if section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    db.session.delete(section)
    db.session.commit()
    flash('Раздел удалён', 'success')
    return redirect(url_for('course.view_course', id=section.course.id))

# Создание активности (с отладкой)
@course.route('/section/<int:section_id>/activity/create', methods=['GET', 'POST'])
@login_required
def create_activity(section_id):
    section = Section.query.get_or_404(section_id)
    if section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = ActivityForm()
    print("request.files =", request.files)
    if form.validate_on_submit():
        max_pos = db.session.query(db.func.max(Activity.position)).filter_by(section_id=section.id).scalar() or -1
        filename = None
        print("=== create_activity ===")
        print("form.file.data =", form.file.data)
        if form.file.data:
            filename = save_activity_file(form.file.data)
            print("filename saved =", filename)
        else:
            print("No file")
        activity = Activity(
            title=form.title.data,
            type=form.type.data,
            content=form.content.data,               # всегда сохраняем описание
            file_path=filename,
            url=form.url.data if form.type.data == 'zoom' else None,
            open_date=moscow_to_utc(form.open_date.data),
            close_date=moscow_to_utc(form.close_date.data),
            position=max_pos + 1,
            section_id=section.id
        )
        db.session.add(activity)
        db.session.commit()
        flash('Элемент добавлен', 'success')
        return redirect(url_for('course.view_course', id=section.course.id))
    else:
        if request.method == 'POST':
            print("Form validation failed. Errors:", form.errors)
    return render_template('course/activity_form.html', form=form, section=section, title='Новый элемент')

# Редактирование активности (с отладкой)
@course.route('/activity/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = ActivityForm(obj=activity)

    if request.method == 'GET':
        form.open_date.data = utc_to_moscow(activity.open_date)
        form.close_date.data = utc_to_moscow(activity.close_date)
    print("request.files =", request.files)
    if form.validate_on_submit():
        print("=== edit_activity ===")
        print("form.file.data =", form.file.data)
        activity.title = form.title.data
        activity.type = form.type.data
        activity.content = form.content.data               # всегда
        activity.url = form.url.data if form.type.data == 'zoom' else None
        activity.open_date = moscow_to_utc(form.open_date.data)
        activity.close_date = moscow_to_utc(form.close_date.data)
        if form.file.data:
            activity.file_path = save_activity_file(form.file.data)
            print("new file saved =", activity.file_path)
        db.session.commit()
        flash('Элемент обновлён', 'success')
        return redirect(url_for('course.view_course', id=activity.section.course.id))
    else:
        if request.method == 'POST':
            print("Form validation failed. Errors:", form.errors)
    return render_template('course/activity_form.html', form=form, section=activity.section, title='Редактирование элемента')

# Удаление активности
@course.route('/activity/<int:id>/delete', methods=['POST'])
@login_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    db.session.delete(activity)
    db.session.commit()
    flash('Элемент удалён', 'success')
    return redirect(url_for('course.view_course', id=activity.section.course.id))

# Просмотр активности
@course.route('/activity/<int:id>')
def view_activity(id):
    activity = Activity.query.get_or_404(id)
    user = current_user if current_user.is_authenticated else None

    if user and user.status in ['user', 'starosta']:
        now = datetime.utcnow()
        if activity.open_date and now < activity.open_date:
            flash('Этот элемент станет доступен позже', 'info')
            return redirect(url_for('course.view_course', id=activity.section.course.id))
        if activity.close_date and now > activity.close_date:
            flash('Срок сдачи истёк', 'warning')

    if activity.type == 'assignment':
        if user and user.status in ['user', 'starosta']:
            submissions = activity.submissions.filter_by(user_id=user.id).order_by(Submission.submitted_at.desc()).all()
        elif user and (user.status in ['teacher', 'enginiger']):
            submissions = activity.submissions.order_by(Submission.submitted_at.desc()).all()
        else:
            submissions = []
        form = SubmissionForm()
        return render_template('course/assignment.html', activity=activity, submissions=submissions, form=form)
    elif activity.type == 'lecture':
        return render_template('course/lecture.html', activity=activity)
    elif activity.type == 'zoom':
        return render_template('course/zoom.html', activity=activity)
    else:
        abort(404)

# Отправка ответа на задание
@course.route('/activity/<int:activity_id>/submit', methods=['POST'])
@login_required
def submit_assignment(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.type != 'assignment':
        abort(400)
    form = SubmissionForm()
    if form.validate_on_submit():
        filename = None
        if form.file.data:
            filename = save_submission_file(form.file.data)
        submission = Submission(
            activity_id=activity.id,
            user_id=current_user.id,
            content=form.content.data,
            file_path=filename
        )
        db.session.add(submission)
        db.session.commit()
        flash('Ответ отправлен', 'success')
    else:
        flash('Ошибка при отправке', 'danger')
    return redirect(url_for('course.view_activity', id=activity.id))

# Оценивание ответа (для преподавателя)
@course.route('/submission/<int:id>/grade', methods=['GET', 'POST'])
@login_required
def grade_submission(id):
    submission = Submission.query.get_or_404(id)
    activity = submission.activity
    if activity.section.course.teacher_id != current_user.id and current_user.status != 'enginiger':
        abort(403)
    form = GradeForm()
    if form.validate_on_submit():
        submission.grade = form.grade.data
        submission.feedback = form.feedback.data
        db.session.commit()
        flash('Оценка сохранена', 'success')
        return redirect(url_for('course.view_activity', id=activity.id))
    form.grade.data = submission.grade
    form.feedback.data = submission.feedback
    return render_template('course/grade_form.html', form=form, submission=submission)