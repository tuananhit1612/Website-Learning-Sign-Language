from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    role = db.Column(db.Enum('user', 'admin'), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)