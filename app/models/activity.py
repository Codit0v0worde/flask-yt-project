from datetime import datetime
from ..extensions import db

class Activity(db.Model):
    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'lecture', 'assignment', 'zoom'
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    open_date = db.Column(db.DateTime, nullable=True)
    close_date = db.Column(db.DateTime, nullable=True)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id', ondelete='CASCADE'), nullable=False)

    submissions = db.relationship('Submission', backref='activity', lazy='dynamic', cascade='all, delete-orphan')