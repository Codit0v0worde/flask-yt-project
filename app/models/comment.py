from datetime import datetime
from ..extensions import db
from .user import User  # относительный импорт модели User

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(200))
    grade = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))

    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))