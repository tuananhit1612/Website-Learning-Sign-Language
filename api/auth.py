from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db
from models.user import User
from authlib.integrations.flask_client import OAuth
import requests
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
auth_bp = Blueprint('auth', __name__)
oauth = OAuth()


google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'email profile'}
)


@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.auth_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google')
def auth_google():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()

    google_id = user_info.get('id')
    email = user_info.get('email')
    name = user_info.get('name')
    avatar = user_info.get('picture')
    

    if not google_id or not email:
        flash("Lỗi khi lấy thông tin Google!", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User(
            name=name,
            email=email,
            google_id=google_id,
            avatar_url=avatar,
            password=None
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["username"] = user.name
    session["role"] = user.role
    session["avatar_url"] = user.avatar_url
    return redirect(url_for("home"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user or not user.password or not check_password_hash(user.password, password):
            flash("Sai email hoặc mật khẩu!", "danger")
            return redirect(url_for("auth.login"))

        session["user_id"] = user.id
        session["role"] = user.role
        session["username"] = user.name
        session["avatar_url"] = user.avatar_url
        flash("Đăng nhập thành công!", "success")
        return redirect(url_for("home"))

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password or not confirm_password:
            flash("Vui lòng điền đầy đủ thông tin!", "danger")
            return redirect(url_for("auth.register"))
        
        if password != confirm_password:
            flash("Mật khẩu không khớp!", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            if existing_user.google_id:
                existing_user.name = name 
                existing_user.password = generate_password_hash(password)
                db.session.commit()

                flash("Tài khoản đã được liên kết với Google, giờ bạn có thể đăng nhập bằng mật khẩu!", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("Email đã tồn tại!", "danger")
                return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công! Mời bạn đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Đăng xuất thành công!", "info")
    return redirect(url_for("auth.login"))
