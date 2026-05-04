from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

# we use .fileName to tell the file that we are calling a file from the same folder
from .models import User, engine
from werkzeug.security import check_password_hash

login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        with Session(engine) as session_db:
            user = session_db.scalars(
                select(User).where(User.username == username)
            ).first()

        if user and check_password_hash(user.password, password):
            if user.role == "vendor" and user.isVerified != "verified":
                error = "Your vendor account is still pending approval."
                return render_template("login.html", error=error)

            session.permanent = True
            session["user_id"] = user.userID
            session["name"] = user.name
            session["username"] = user.username
            session["role"] = user.role
            session["is_verified"] = user.isVerified
            return redirect(url_for("index.index"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)
