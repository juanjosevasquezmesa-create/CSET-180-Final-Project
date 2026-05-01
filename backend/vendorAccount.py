from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, engine
from werkzeug.security import check_password_hash

vendor_account_bp = Blueprint("vendor_account", __name__, url_prefix="/account/")


@vendor_account_bp.route("vendor", methods=["GET", "POST"])
def vendor_account():
    if not session:
        pass # some sort of logic to prompt the user to go back to the login page
    if session["role"] != "customer":
        pass # some sort of logic to prompt the user to go back to the main page
# accounts page functionality for vendor users
