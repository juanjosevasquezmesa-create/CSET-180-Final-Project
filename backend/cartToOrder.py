from flask import Blueprint, session, redirect, url_for, flash
from sqlalchemy.orm import Session

from .models import CartItem, Order, OrderItem, engine


cartToOrder_bp = Blueprint("recipt", __name__)



# Existing products page
@cartToOrder_bp.route("/recipt", methods=["GET"])
def cartToOrder():
    return redirect(url_for("cartPage.view_cart"))


# New checkout endpoint
@cartToOrder_bp.route("/checkout", methods=["POST"])
def checkout():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to checkout.")
        return redirect(url_for("cartPage.view_cart"))

    if session.get("role") != "customer":
        flash("Only customer accounts can checkout.")
        return redirect(url_for("index.index"))

    with Session(engine) as session_db:
        cart_items = session_db.query(CartItem).filter_by(customer_id=user_id).all()
        if not cart_items:
            flash("Your cart is empty.")
            return redirect(url_for("cartPage.view_cart"))

        total_price = 0
        order_items = []
        cart_items_to_clear = []
        for item in cart_items:
            if not item.variation or not item.variation.product:
                session_db.delete(item)
                continue

            if item.quantity > item.variation.stock:
                flash(f"Only {item.variation.stock} of {item.variation.product.model} is available.")
                return redirect(url_for("cartPage.view_cart"))

            # Get price from variation's product
            price = float(item.variation.product.price)
            total_price += price * item.quantity
            order_items.append({
                "var_id": item.var_id,
                "quantity": item.quantity,
                "price": price,
                "variation": item.variation,
            })
            cart_items_to_clear.append(item)

        if not order_items:
            session_db.commit()
            flash("Your cart no longer has any available items.")
            return redirect(url_for("cartPage.view_cart"))

        # Create order
        order = Order(customer_id=user_id, total_price=total_price, status="pending")
        session_db.add(order)
        session_db.flush()  # Get order_id

        # Add order items
        for oi in order_items:
            order_item = OrderItem(
                order_id=order.order_id,
                var_id=oi["var_id"],
                quantity=oi["quantity"],
                price=oi["price"]
            )
            session_db.add(order_item)
            oi["variation"].stock -= oi["quantity"]

        # Clear cart
        for item in cart_items_to_clear:
            session_db.delete(item)

        session_db.commit()

        flash("Order placed successfully!")
        return redirect(url_for("cartPage.view_cart"))
