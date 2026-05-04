from flask import Blueprint, flash, redirect, render_template, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import Product, engine

vendor_Account_bp = Blueprint("vAccount", __name__, url_prefix="/account/")


@vendor_account_bp.route("", methods=["GET"])
def account_home():
    if not session.get("user_id"):
        return redirect(url_for("login.login"))

    role = session.get("role")
    if role not in {"admin", "vendor", "customer"}:
        with Session(engine) as session_db:
            user = session_db.get(User, session["user_id"])
            if user:
                session["role"] = user.role
                role = user.role

    if role in {"admin", "vendor", "customer"}:
        return redirect(url_for(f"{role}_account.{role}_account"))

    return redirect(url_for("index.index"))


@vendor_account_bp.route("vendor", methods=["GET", "POST"])
def vendor_account():
    if not session.get("user_id"):
        flash("Please log in to view your account.", "error")
        return redirect(url_for("login.login"))

    with Session(engine) as session_db:
        vendor = session_db.get(User, session["user_id"])
        if not vendor or vendor.role != "vendor":
            return redirect(url_for("index.index"))

        session["role"] = vendor.role
        products = session_db.scalars(
            select(Product)
            .options(selectinload(Product.variations))
            .where(Product.vendor_id == session["user_id"])
            .order_by(Product.product_id.desc())
        ).all()

    return render_template("vendorAccount.html", user=vendor, products=products)
