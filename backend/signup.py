from flask import Blueprint, render_template, redirect, request, url_for
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from .models import User, engine
from .config import flash_message


signup_bp = Blueprint("signup", __name__, url_prefix="/signup")


@signup_bp.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get('name', "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")


        if not username or not email or not password or not name:
            flash_message("All fields are required.", "error")
        else:
            with Session(engine) as session_db:
                existing_user = session_db.scalars(
                    select(User).where(
                        # this acts like an or statement whereever the , is
                        or_(User.username == username, User.email == email)
                    )
                ).first()

                if existing_user:
                    flash_message("That username or email is already in use.", "error")
                else:
                    session_db.add(
                        User(
                            name=name,
                            username=username,
                            email=email,
                            password=generate_password_hash(password),
                        )
                    )
                    session_db.commit()
                    flash_message("Signup successful! Please log in.", "success")
                    return redirect(url_for("login.login"))

    return render_template("signup.html")
