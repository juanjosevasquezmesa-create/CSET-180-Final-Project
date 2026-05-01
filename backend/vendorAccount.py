from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

# we use .fileName to tell the file that we are calling a file from the same folder
from .models import User, engine
from werkzeug.security import check_password_hash

vAccount_bp = Blueprint("vAccount", __name__, url_prefix="/account/")


@vAccount_bp.route("vendor", methods=["GET", "POST"])
def vendorAcc():
    if not session:
        pass # some sort of logic to prompt the user to go back to the login page
    if session["role"] != "customer":
        pass # some sort of logic to prompt the user to go back to the main page