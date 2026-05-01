# Hub for customer account functions

from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, engine
from werkzeug.security import check_password_hash

customer_account_bp = Blueprint("customer_account", __name__, url_prefix="/account/")


@customer_account_bp.route("customer", methods=["GET", "POST"])
def customer_account():
    if not session:
        pass # some sort of logic to prompt the user to go back to the login page
    if session["role"] != "customer":
        pass # some sort of logic to prompt the user to go back to the main page
# customer accounts page functionality for customer users
