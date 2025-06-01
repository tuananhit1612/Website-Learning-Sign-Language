from models.database import db

class LessonQuestion(db.Model):
    __tablename__ = 'lesson_questions'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    video_id = db.Column(db.String(50), db.ForeignKey('sign_videos.id'), nullable=False)
    type = db.Column(db.Enum('text', 'video','learning'), nullable=False)

    lesson = db.relationship('Lesson', backref='questions')
    video = db.relationship('SignVideo', backref='questions')
