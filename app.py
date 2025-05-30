
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models.database import db
from flask import Flask, render_template, request, session, jsonify
from models.user import User
import os
from models.chapter import Chapter
from models.lesson import Lesson
from api.auth import auth_bp
from api.videos import video_bp
from api.learning import learning_bp
from api.admin import admin_bp
from api.auth import auth_bp, oauth
from api.siformer_vnsl import siformer_vnsl_bp
from models.user_progress import UserProgress
from models.lesson_question import LessonQuestion


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = os.urandom(24)

db.init_app(app)

CORS(app)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(video_bp)
app.register_blueprint(learning_bp)
app.register_blueprint(siformer_vnsl_bp)
oauth.init_app(app)
@app.cli.command("create-db")
def create_db():
    db.create_all()
    print("Database tables created")

@app.route("/")
def home():

    return render_template("index.html")

@app.route("/practice")
def practice():
    return render_template("practice.html")

@app.route("/lessons")
def lessons():
    if session.get("user_id") is None:
        return render_template("login.html")
    return render_template("lessons.html")

@app.route("/dictionary")
def dictionary():
    if session.get("user_id") is None:
        return render_template("login.html")
    return render_template("dictionary.html")

if __name__ == "__main__":
    app.run(debug=True)
