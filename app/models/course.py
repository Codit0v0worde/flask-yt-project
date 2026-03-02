from datetime import datetime
from ..extensions import db

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('courses', lazy='dynamic'))
    sections = db.relationship('Section', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    