from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

# Импортируем модель User для валидации логина
from .models.user import User

# ... остальные импорты, если есть

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
    """Form to log in users"""
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class StudentForm(FlaskForm):
    subject = StringField('Тема', validators=[DataRequired()], render_kw={'class': 'form-control'})
    student = SelectField('Студент', coerce=int, validators=[DataRequired()], render_kw={'class': 'form-control'})


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
    parent_id = HiddenField()  # для ответов на комментарии
    submit = SubmitField('Отправить')