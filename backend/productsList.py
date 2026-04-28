from flask import Blueprint, render_template, redirect, request, url_for
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from .models import User, Product, engine
from .config import flash_message


productList_bp = Blueprint("productList", __name__, url_prefix="/signup")


@productList_bp.route("/", methods=["GET"])
def signup():

    with Session(engine) as session_db:
        existing_user = session_db.scalars(
            select(User.name).where(User.user_id == Product.vendor_id)
                
        ).all()

        if existing_user:
            flash_message("That username or email is already in use.", "error")
        else:
            flash_message("Signup successful! Please log in.", "success")
            return redirect(url_for("login.login"))

    return render_template("signup.html")
