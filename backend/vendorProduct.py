from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, session, url_for, request
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload

from .models import CartItem, OrderItem, Product, ProductVariation, User,  engine

vendorProduct_bp = Blueprint("vendorProduct", __name__, url_prefix="/account/vendor/")

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

@vendorProduct_bp.route("add", methods=["GET", "POST"])
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

@vendorProduct_bp.route("<int:product_id>/delete", methods=["GET"])
def productDelConfirm(product_id):
    if not session.get("user_id"):
        flash("Please log in to delete products.", "error")
        return redirect(url_for("login.login"))

    if session.get("role") != "vendor":
        flash("Only vendors can delete products.", "error")
        return redirect(url_for("index.index"))

    with Session(engine) as session_db:
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
            select(Product).where(Product.product_id == product_id)
        ).first()

        if product is None:
            abort(404)

        return render_template("vendorDelete.html", product=product)


@vendorProduct_bp.route("<int:product_id>/delete", methods=["POST"])
def productDel(product_id):
    if not session.get("user_id"):
        flash("Please log in to delete products.", "error")
        return redirect(url_for("login.login"))

    if session.get("role") != "vendor":
        flash("Only vendors can delete products.", "error")
        return redirect(url_for("index.index"))

    with Session(engine) as session_db:
        productUser = session_db.scalars(
            select(User.user_id)
            .join(Product, User.user_id == Product.vendor_id)
            .where(Product.product_id == product_id)
        ).first()
        
        if productUser is None:
            abort(404)

        if productUser != session.get("user_id"):
            abort(403)

        productVariations = select(ProductVariation.var_id).where(
            ProductVariation.product_id == product_id
        )
        cartItemsDelete = delete(CartItem).where(CartItem.var_id.in_(productVariations))
        productDelete = delete(Product).where(Product.product_id == product_id)

        session_db.execute(cartItemsDelete)
        session_db.execute(productDelete)
        session_db.commit()
        flash("Product deleted successfully.", "success")
        
        return redirect(url_for("vAccount.vendorAcc"))

@vendorProduct_bp.route("<int:product_id>/edit", methods=["GET", "POST"])
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

        session_db.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for("vAccount.vendorAcc"))
