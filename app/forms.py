from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField , PasswordField , SubmitField , FileField , BooleanField , SelectField
from wtforms.validators import  DataRequired , Length , Email , EqualTo , ValidationError

from .models.user import User

class RegistrationForm(FlaskForm):
    name=StringField('ФИО' , validators=[DataRequired() , Length(min=2, max=100)])
    login=StringField('Логин',validators=[DataRequired() , Length(min=2, max=20)])
    password=PasswordField('Пароль' ,validators=[DataRequired()])
    confirm_password=PasswordField('Потвердите пароль',validators=[DataRequired(),EqualTo('password')])
    avatar=FileField('Загрузите аватарку' , validators=[FileAllowed(['jpg' , 'jpeg' , 'png'])])
    submit=SubmitField('Зарегистрироваться')
    
    def validate_login(self,login):
        user=User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError("Эй,у нас не разрешаются клоны(данное имя занято).Придумай что нибудь другое")

class LoginForm(FlaskForm):
    """Form to log in users"""
    login=StringField('Логин',validators=[DataRequired(),Length(min=2 , max=20)])
    password=PasswordField('Пароль',validators=[DataRequired()])
    remember=BooleanField('Запомнить меня')
    submit=SubmitField('Войти')


class StudentForm(FlaskForm):
    subject = StringField('Тема', validators=[DataRequired()], render_kw={'class': 'form-control'})
    student = SelectField('Студент', coerce=int, validators=[DataRequired()], render_kw={'class': 'form-control'})
    
class TeacherForm(FlaskForm):
    teacher = SelectField('Преподаватель', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Показать')