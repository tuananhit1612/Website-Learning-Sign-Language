from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db
from models.sign_videos import SignVideo
from models.category import Category

video_bp = Blueprint('video', __name__)

@video_bp.route("/dictionary", methods=["GET"])
def videos():
    categories = Category.query.all()
    videos = SignVideo.query.all()
    return render_template("dictionary.html", videos=videos, categories=categories)

@video_bp.route("/dictionary/category/<int:category_id>", methods=["GET"])
def videos_by_category(category_id):
    categories = Category.query.all()
    videos = SignVideo.query.filter_by(category_id=category_id).all()
    return render_template("dictionary.html", videos=videos, categories=categories, selected_category=category_id)

@video_bp.route("/videos/<string:video_id>", methods=["GET"])
def video_detail(video_id):
    video = SignVideo.query.get_or_404(video_id)
    return render_template("video_detail.html", video=video)

@video_bp.route("/dictionary/title/<string:title>", methods=["GET"])
def video_by_title(title):
    categories = Category.query.all()
    videos = SignVideo.query.filter_by(title=title).all()
    return render_template("dictionary.html", videos=videos, categories=categories)
