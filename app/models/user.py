from datetime import datetime
from ..extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='user')
    name = db.Column(db.String(50))
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200))

    # Отношение к постам, где пользователь является преподавателем
    teacher_posts = db.relationship('Post', foreign_keys='Post.teacher', back_populates='teacher_user')
    
