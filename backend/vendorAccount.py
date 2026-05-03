from flask import Blueprint, flash, redirect, render_template, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import Product, engine

vendor_Account_bp = Blueprint("vAccount", __name__, url_prefix="/account/")


@vendor_Account_bp.route("vendor", methods=["GET"])
def vendorAcc():
    if not session.get("user_id"):
        flash("Please log in to view your vendor account.", "error")
        return redirect(url_for("login.login"))

    if session.get("role") != "vendor":
        flash("Only vendor accounts can view that page.", "error")
        return redirect(url_for("index.index"))

    with Session(engine) as session_db:
        products = session_db.scalars(
            select(Product)
            .options(selectinload(Product.variations))
            .where(Product.vendor_id == session.get("user_id"))
            .order_by(Product.product_id)
        ).all()

    return render_template("vendorAccount.html", products=products)
# accounts page functionality for vendor users