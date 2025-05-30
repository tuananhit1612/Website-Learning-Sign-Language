from .database import db

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image =  db.Column(db.String(255), nullable=False)
    lessons = db.relationship('Lesson', backref='chapter', lazy=True)
