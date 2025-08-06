from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    videos = db.relationship('Video', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'plan': self.plan,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    youtube_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clips = db.relationship('Clip', backref='video', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'youtube_url': self.youtube_url,
            'title': self.title,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'clips_count': len(self.clips)
        }

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    file_path = db.Column(db.String(500))
    thumbnail_path = db.Column(db.String(500))
    duration = db.Column(db.Float)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'file_path': self.file_path,
            'thumbnail_path': self.thumbnail_path,
            'duration': self.duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 