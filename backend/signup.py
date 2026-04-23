from flask import Blueprint, render_template, redirect, request, url_for
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from backend.models import User, engine


signup_bp = Blueprint("signup", __name__, url_prefix="/signup")


@signup_bp.route("/", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            error = "All fields are required."
        else:
            with Session(engine) as session_db:
                existing_user = session_db.scalars(
                    select(User).where(
                        or_(User.username == username, User.email == email)
                    )
                ).first()

                if existing_user:
                    error = "That username or email is already in use."
                else:
                    session_db.add(
                        User(
                            username=username,
                            email=email,
                            password=generate_password_hash(password),
                        )
                    )
                    session_db.commit()
                    return redirect(url_for("login.login"))

    return render_template("signup.html", error=error)
