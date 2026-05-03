from flask import Blueprint, abort, flash, redirect, render_template, session, url_for
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from .models import CartItem, Product, ProductVariation, User,  engine


productDel_bp = Blueprint("productDel", __name__, url_prefix="/account/vendor/")


@productDel_bp.route("<int:product_id>/delete", methods=["GET"])
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


@productDel_bp.route("<int:product_id>/delete", methods=["POST"])
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
        
        return redirect(url_for("vendor_account.vendor_account"))
