# admin.py
from flask import Blueprint, render_template, request,session, redirect, url_for, flash
from models.database import db
from models.chapter import Chapter
from models.lesson import Lesson
from models.lesson_question import LessonQuestion
from models.sign_videos import SignVideo

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/lessons')
def manage_lessons():
    if 'user_id' not in session:
        flash('Bạn cần đăng nhập để truy cập trang này!', 'danger')
        return redirect(url_for('auth.login'))
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('home'))
    lessons = Lesson.query.all()
    chapters = Chapter.query.all()
    return render_template('admin/lessons.html', lessons=lessons, chapters=chapters)


@admin_bp.route('/admin/lessons/add', methods=['POST'])
def add_lesson():
    chapter_id = request.form.get('chapter_id')
    title = request.form.get('title')
    content = request.form.get('content')

    new_lesson = Lesson(chapter_id=chapter_id, title=title, content=content)
    db.session.add(new_lesson)
    db.session.commit()

    flash('Đã thêm bài học mới!', 'success')
    return redirect(url_for('admin.manage_lessons'))


@admin_bp.route('/admin/lessons/edit/<int:lesson_id>', methods=['POST'])
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    lesson.chapter_id = request.form.get('chapter_id')
    lesson.title = request.form.get('title')
    lesson.content = request.form.get('content')

    db.session.commit()

    flash('Đã cập nhật bài học!', 'success')
    return redirect(url_for('admin.manage_lessons'))
@admin_bp.route('/admin/lessons/delete/<int:lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()

    flash('Đã xoá bài học!', 'info')
    return redirect(url_for('admin.manage_lessons'))

@admin_bp.route('/admin/lessons/<int:lesson_id>/questions')
def manage_questions(lesson_id):
    if 'user_id' not in session:
        flash('Bạn cần đăng nhập để truy cập trang này!', 'danger')
        return redirect(url_for('auth.login'))
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('home'))
    lesson = Lesson.query.get_or_404(lesson_id)
    questions = LessonQuestion.query.filter_by(lesson_id=lesson_id).all()
    sign_videos = SignVideo.query.all()
    return render_template('admin/questions.html', lesson=lesson, questions=questions, sign_videos=sign_videos)


@admin_bp.route('/admin/lessons/<int:lesson_id>/questions/add', methods=['POST'])
def add_question(lesson_id):
    video_id = request.form.get('video_id')
    q_type = request.form.get('type')
    
    new_question = LessonQuestion(lesson_id=lesson_id, video_id=video_id, type=q_type)
    db.session.add(new_question)
    db.session.commit()

    flash('Đã thêm câu hỏi mới!', 'success')
    return redirect(url_for('admin.manage_questions', lesson_id=lesson_id))


@admin_bp.route('/admin/lessons/<int:lesson_id>/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(lesson_id, question_id):

    question = LessonQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()

    flash('Đã xoá câu hỏi!', 'info')
    return redirect(url_for('admin.manage_questions', lesson_id=lesson_id))
