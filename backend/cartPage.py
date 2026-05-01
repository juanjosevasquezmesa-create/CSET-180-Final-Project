from flask import Blueprint, redirect, render_template, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import CartItem, ProductVariation, engine


cart_page_bp = Blueprint("cartPage", __name__, url_prefix="/cart")


@cart_page_bp.route("/", methods=["GET"])
def view_cart():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    with Session(engine) as session_db:
        cart_items = session_db.scalars(
            select(CartItem)
            .where(CartItem.customer_id == session["user_id"])
            .options(
                selectinload(CartItem.variation).selectinload(ProductVariation.product)
            )
            .order_by(CartItem.cart_item_id)
        ).all()

        subtotal = sum(
            float(item.variation.product.price) * item.quantity for item in cart_items
        )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        session=session,
    )
