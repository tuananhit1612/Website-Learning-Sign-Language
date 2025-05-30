from .database import db

class SignVideo(db.Model):
    __tablename__ = 'sign_videos'

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<SignVideo {self.title}>"
