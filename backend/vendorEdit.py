from decimal import Decimal, InvalidOperation
import os

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from werkzeug.utils import secure_filename

from .models import OrderItem, Product, ProductVariation, User, engine

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "images", "products")
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)

def _allowed_image(image_file):
    filename = image_file.filename or ""
    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    mimetype = image_file.mimetype or ""
    return mimetype.startswith("image/")


def _save_product_image(product_id, image):
    if not image or not image.filename:
        return None

    if not _allowed_image(image):
        return None

    ext = secure_filename(image.filename).rsplit(".", 1)[1].lower()
    filename = f"product_{product_id}.{ext}"
    filepath = os.path.join(IMAGE_UPLOAD_FOLDER, filename)

    for old_ext in ALLOWED_IMAGE_EXTENSIONS:
        old_path = os.path.join(IMAGE_UPLOAD_FOLDER, f"product_{product_id}.{old_ext}")
        if old_path != filepath and os.path.exists(old_path):
            os.remove(old_path)

    image.stream.seek(0)
    image.save(filepath)
    return filename


productEdit_bp = Blueprint("productEdit", __name__, url_prefix="/account/vendor/")


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


@productEdit_bp.route("<int:product_id>/edit", methods=["GET", "POST"])
def productEdit(product_id):
    if session.get("role") != "vendor":
        flash("You must be logged in as a vendor to edit products.", "error")
        return redirect(url_for("login.login"))

    with Session(engine) as session_db:
        product = _get_vendor_product(session_db, product_id)

        if request.method == "GET":
            return render_template("vendorEdit.html", product=product)

        model = request.form.get("model", "").strip()
        description = _clean_text(request.form.get("description", ""))
        warranty_period = _clean_text(request.form.get("warranty_period", ""))
        price_text = request.form.get("price", "").strip()

        if not model or not price_text:
            flash("Model and price are required.", "error")
            return render_template("vendorEdit.html", product=product), 400

        try:
            price = Decimal(price_text)
        except InvalidOperation:
            flash("Price must be a valid number.", "error")
            return render_template("vendorEdit.html", product=product), 400

        product.model = model
        product.description = description
        product.warranty_period = warranty_period
        product.price = price

        selected_variation_ids = set(request.form.getlist("selected_variations"))

        for variation in list(product.variations):
            variation_id = str(variation.var_id)

            if variation_id not in selected_variation_ids:
                hasOrders = session_db.scalars(
                    select(OrderItem.order_item_id).where(
                        OrderItem.var_id == variation.var_id
                    )
                ).first()

                if hasOrders:
                    variation.stock = 0
                    continue

                session_db.delete(variation)
                continue

            color = request.form.get(f"color_{variation_id}", "").strip()
            year = request.form.get(f"year_{variation_id}", "").strip()
            stock_text = request.form.get(f"stock_{variation_id}", "").strip()

            if not color or not year or not stock_text:
                flash("Selected variations need color, year, and stock.", "error")
                return render_template("vendorEdit.html", product=product), 400

            try:
                stock = int(stock_text)
            except ValueError:
                flash("Variation stock must be a whole number.", "error")
                return render_template("vendorEdit.html", product=product), 400

            variation.color = color
            variation.year = year
            variation.stock = stock

        new_colors = request.form.getlist("new_color")
        new_years = request.form.getlist("new_year")
        new_stocks = request.form.getlist("new_stock")

        for color, year, stock_text in zip(new_colors, new_years, new_stocks):
            color = color.strip()
            year = year.strip()
            stock_text = stock_text.strip()

            if not color and not year and not stock_text:
                continue

            if not color or not year or not stock_text:
                flash("New variations need color, year, and stock.", "error")
                return render_template("vendorEdit.html", product=product), 400

            try:
                stock = int(stock_text)
            except ValueError:
                flash("New variation stock must be a whole number.", "error")
                return render_template("vendorEdit.html", product=product), 400

            session_db.add(
                ProductVariation(
                    product_id=product.product_id,
                    color=color,
                    year=year,
                    stock=stock,
                )
            )

        image = request.files.get("image")
        if image and image.filename:
            saved_filename = _save_product_image(product.product_id, image)
            if not saved_filename:
                session_db.rollback()
                flash("Upload must be a valid image file (jpg, jpeg, png, webp, gif).", "error")
                return render_template("vendorEdit.html", product=product), 400

        session_db.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for("vendor_account.vendor_account"))
