# This one needs to show all vendors and allows the admin to click a button for pending vendors to verify them

from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

# we use .fileName to tell the file that we are calling a file from the same folder
from .models import User, engine
from werkzeug.security import check_password_hash

aAccount_bp = Blueprint("aAccount", __name__, url_prefix="/account/")


@aAccount_bp.route("admin", methods=["GET", "POST"])
def adminAcc():
    if not session:
        pass # some sort of logic to prompt the user to go back to the login page
    if session["role"] != "admin":
        pass # some sort of logic to prompt the user to go back to the main page