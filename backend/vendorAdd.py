from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, session, url_for, abort
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import OrderItem, Product, ProductVariation, User, engine


productAdd_bp = Blueprint("productAdd", __name__, url_prefix="/account/vendor/")

def _get_vendor_product(session_db, product_id):
    productUser = session_db.scalars(
        select(User.user_id)
        .join(Product, User.user_id == Product.vendor_id)
        .where(Product.product_id == product_id)
    ).first()

    if productUser is None:
        abort(404)

    if productUser != session.get("user_id"):
        abort(403)

    product = session_db.scalars(
        select(Product)
        .options(selectinload(Product.variations))
        .where(Product.product_id == product_id)
    ).first()

    if product is None:
        abort(404)

    return product


def _clean_text(value):
    value = value.strip()
    return value or None


@productAdd_bp.route("add", methods=["GET", "POST"])
def productAdd():
    if not session.get("user_id"):
        flash("Please log in to add products.", "error")
        return redirect(url_for("login.login"))

    if session.get("role") != "vendor":
        flash("Only vendors can add products.", "error")
        return redirect(url_for("index.index"))

    if request.method == "GET":
        return render_template("vendorAdd.html")

    model = request.form.get("model", "").strip()
    description = request.form.get("description", "").strip() or None
    warranty_period = request.form.get("warranty_period", "").strip() or None
    price_text = request.form.get("price", "").strip()

    if not model or not price_text:
        flash("Model and price are required.", "error")
        return render_template("vendorAdd.html"), 400

    try:
        price = Decimal(price_text)
    except InvalidOperation:
        flash("Price must be a valid number.", "error")
        return render_template("vendorAdd.html"), 400

    colors = request.form.getlist("color")
    years = request.form.getlist("year")
    stocks = request.form.getlist("stock")

    variations = []
    for color, year, stock_text in zip(colors, years, stocks):
        color = color.strip()
        year = year.strip()
        stock_text = stock_text.strip()

        if not color and not year and not stock_text:
            continue

        if not color or not year or not stock_text:
            flash("Each variation needs color, year, and stock.", "error")
            return render_template("vendorAdd.html"), 400

        try:
            stock = int(stock_text)
        except ValueError:
            flash("Variation stock must be a whole number.", "error")
            return render_template("vendorAdd.html"), 400

        variations.append(ProductVariation(color=color, year=year, stock=stock))

    with Session(engine) as session_db:
        product = Product(
            vendor_id=session.get("user_id"),
            model=model,
            description=description,
            warranty_period=warranty_period,
            price=price,
            created_by=session.get("user_id"),
            variations=variations,
        )
        session_db.add(product)
        session_db.commit()

    flash("Product added successfully.", "success")
    return redirect(url_for("vAccount.vendorAcc"))
