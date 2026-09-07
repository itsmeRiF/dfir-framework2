from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
from models.user import User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _safe_next():
    """The page the visitor was heading for before being asked to log in.

    Only a path on this site is honoured — an absolute URL in `next`
    would turn the login form into an open redirect.
    """

    target = request.args.get("next", "")

    if target.startswith("/") and not target.startswith("//"):
        return target

    return url_for("dashboard.dashboard")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(_safe_next())
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
