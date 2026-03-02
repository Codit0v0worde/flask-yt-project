from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, SelectField, HiddenField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, URL, NumberRange
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

from .models.user import User

# Для множественного выбора студентов (используется в StudentForm)
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# ========== Существующие формы ==========

class RegistrationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Загрузите аватарку', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError("Эй, у нас не разрешаются клоны (данное имя занято). Придумай что нибудь другое")

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class StudentForm(FlaskForm):
    subject = StringField('Тема', validators=[DataRequired()], render_kw={'class': 'form-control'})
    students = MultiCheckboxField('Студенты', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.students.choices = [(u.id, u.name) for u in User.query.filter_by(status='user').all()]

class TeacherForm(FlaskForm):
    teacher = SelectField('Преподаватель', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Показать')

class ManageUserForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    status = SelectField('Статус', choices=[
        ('user', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('starosta', 'Староста'),
        ('enginiger', 'Суперпользователь')
    ], validators=[DataRequired()])
    submit = SubmitField('Изменить')

class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    avatar = FileField('Новый аватар', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')])
    old_password = PasswordField('Старый пароль')
    new_password = PasswordField('Новый пароль', validators=[EqualTo('confirm_password', message='Пароли не совпадают')])
    confirm_password = PasswordField('Подтвердите новый пароль')
    submit = SubmitField('Сохранить')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired()], render_kw={'rows': 3})
    file = FileField('Прикрепить файл', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'], 'Недопустимый формат файла')])
    grade = SelectField('Оценка', choices=[('', 'Без оценки')] + [(str(i), str(i)) for i in range(1, 6)], validators=[Optional()])
    parent_id = HiddenField()
    submit = SubmitField('Отправить')

# ========== Новые формы для курсов ==========

class CourseForm(FlaskForm):
    title = StringField('Название курса', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить')

class SectionForm(FlaskForm):
    title = StringField('Название раздела', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить')

class ActivityForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=200)])
    type = SelectField('Тип', choices=[
        ('lecture', 'Лекция'),
        ('assignment', 'Задание'),
        ('zoom', 'Ссылка на Zoom')
    ], validators=[DataRequired()])
    content = TextAreaField('Текст лекции', validators=[Optional()])
    file = FileField('Прикрепить файл', validators=[FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'png'], 'Недопустимый формат')])
    url = StringField('Ссылка на Zoom', validators=[Optional(), URL()])
    open_date = DateTimeField('Дата открытия', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    close_date = DateTimeField('Дата закрытия', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Сохранить')

class SubmissionForm(FlaskForm):
    content = TextAreaField('Ваш ответ', validators=[Optional()])
    file = FileField('Прикрепить файл', validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'], 'Недопустимый формат')])
    submit = SubmitField('Отправить')

class GradeForm(FlaskForm):
    grade = IntegerField('Оценка', validators=[Optional(), NumberRange(min=1, max=10)])
    feedback = TextAreaField('Комментарий', validators=[Optional()])
    submit = SubmitField('Сохранить оценку')