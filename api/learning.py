from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import db
from models.lesson_question import LessonQuestion
from models.sign_videos import SignVideo
from models.user_progress import UserProgress
from models.chapter import Chapter
from models.lesson import Lesson
from sqlalchemy import func

learning_bp = Blueprint('learning', __name__)

@learning_bp.route("/learn", methods=["GET"])
def learn():
    user_id = session.get("user_id")
    if user_id is None:
        flash("Vui lòng đăng nhập để xem tiến độ học tập của bạn.", "danger")
        return redirect(url_for("auth.login"))
    chapters = Chapter.query.all()
    return render_template("learn.html", chapters=chapters)

@learning_bp.route("/lessons/<int:chapter_id>", methods=["GET"])
def lessons_by_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    lessons = Lesson.query.filter_by(chapter_id=chapter_id).order_by(Lesson.id).all()
    user_id = session.get("user_id")

    if user_id is None:
        flash("Vui lòng đăng nhập để xem tiến độ học tập của bạn.", "danger")
        return redirect(url_for("auth.login"))

    last_lesson_id = db.session.query(func.max(UserProgress.lesson_id)).filter_by(
        user_id=user_id, chapter_id=chapter_id, status=True
    ).scalar()

    if last_lesson_id:
        current_lesson = Lesson.query.filter(
            Lesson.chapter_id == chapter_id,
            Lesson.id > last_lesson_id
        ).order_by(Lesson.id.asc()).first()
    else:
        current_lesson = Lesson.query.filter_by(chapter_id=chapter_id).order_by(Lesson.id.asc()).first()

    current_lesson_id = current_lesson.id if current_lesson else None

    unlocked_lessons = Lesson.query.filter(
        Lesson.chapter_id == chapter_id,
        Lesson.id <= current_lesson_id
    ).all() if current_lesson_id else []

    return render_template("lessons.html",
                           chapter=chapter,
                           lessons=lessons,
                           unlocked_lessons=unlocked_lessons,
                           current_lesson_id=current_lesson_id)

@learning_bp.route("/lessons/<int:chapter_id>/<int:lesson_id>")
def learn_lesson(chapter_id, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id, chapter_id=chapter_id).first_or_404()
    questions = LessonQuestion.query.filter_by(lesson_id=lesson_id).all()

    question_data = []
    for q in questions:
        video = SignVideo.query.get(q.video_id)
        question_data.append({
            "id": q.id,
            "type": q.type,
            "video": {
                "id": video.id,
                "title": video.title,
                "url": video.video_url
            }
        })

    return render_template("quiz.html", lesson=lesson, questions=question_data, chapter_id=chapter_id, lesson_id=lesson_id)

@learning_bp.route("/api/progress", methods=["POST"])
def update_progress():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    user_id = session["user_id"]
    chapter_id = data.get("chapter_id")
    lesson_id = data.get("lesson_id")

    if not chapter_id or not lesson_id:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    existing = UserProgress.query.filter_by(
        user_id=user_id,
        chapter_id=chapter_id,
        lesson_id=lesson_id
    ).first()

    if existing:
        existing.status = True
    else:
        new_progress = UserProgress(
            user_id=user_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            status=True
        )
        db.session.add(new_progress)

    db.session.commit()
    return jsonify({"message": "Cập nhật thành công"})
