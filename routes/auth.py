
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash

from models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Already logged in? Go to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Find the account by username
        user = User.query.filter_by(username=username).first()

        # Verify the password against its stored hash
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard_page"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
