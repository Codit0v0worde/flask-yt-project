from datetime import datetime
from ..extensions import db

# Ассоциативная таблица для связи Post и User (студенты)
post_students = db.Table('post_students',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    subject = db.Column(db.String(250))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(200), nullable=True)

    # Связь с преподавателем (back_populates)
    teacher_user = db.relationship('User', foreign_keys=[teacher], back_populates='teacher_posts')
    # Связь со студентами (многие ко многим)
    students = db.relationship('User', secondary=post_students, backref=db.backref('assigned_posts', lazy='dynamic'), lazy='dynamic')