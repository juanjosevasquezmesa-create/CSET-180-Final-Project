from flask import Blueprint, flash, redirect, render_template, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import CartItem, ProductVariation, engine


cart_page_bp = Blueprint("cartPage", __name__, url_prefix="/cart")


@cart_page_bp.route("/", methods=["GET"])
def view_cart():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    if session.get("role") != "customer":
        flash("Only customer accounts can view the cart.", "error")
        return redirect(url_for("index.index"))

    with Session(engine) as session_db:
        cart_items = session_db.scalars(
            select(CartItem)
            .where(CartItem.customer_id == session["user_id"])
            .options(
                selectinload(CartItem.variation).selectinload(ProductVariation.product)
            )
            .order_by(CartItem.cart_item_id)
        ).all()

        visible_cart_items = []
        subtotal = 0

        for item in cart_items:
            if not item.variation.product:
                session_db.delete(item)
                continue

            visible_cart_items.append(item)
            subtotal += float(item.variation.product.price) * item.quantity

        if len(visible_cart_items) != len(cart_items):
            session_db.commit()

    return render_template(
        "cart.html",
        cart_items=visible_cart_items,
        subtotal=subtotal,
        session=session,
    )
