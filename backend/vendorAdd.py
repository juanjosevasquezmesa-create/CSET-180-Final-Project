from decimal import Decimal, InvalidOperation
import os

from flask import Blueprint, flash, redirect, render_template, request, session, url_for, abort
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
        session_db.flush()

        image = request.files.get("image")
        if image and image.filename:
            saved_filename = _save_product_image(product.product_id, image)
            if not saved_filename:
                session_db.rollback()
                flash("Upload must be a valid image file (jpg, jpeg, png, webp, gif).", "error")
                return render_template("vendorAdd.html"), 400

        session_db.commit()

    flash("Product added successfully.", "success")
    return redirect(url_for("vendor_account.vendor_account"))
