# Hub for customer account functions

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, Order, OrderItem, Product, Review, Complaint, engine
from werkzeug.security import check_password_hash

customer_account_bp = Blueprint("customer_account", __name__, url_prefix="/account/")


@customer_account_bp.route("customer", methods=["GET"])
def customer_account():
    if not session:
        return redirect(url_for("login.login"))
    if session.get("role") != "customer":
        return redirect(url_for("index.index"))

    user_id = session["user_id"]
    with Session(engine) as session_db:
        user = session_db.get(User, user_id)
        if not user:
            return redirect(url_for("login.login"))

        # Get all orders for the customer
        orders = session_db.scalars(
            select(Order).where(Order.customer_id == user_id).order_by(Order.order_date.desc())
        ).all()

        # Prepare order data with items
        order_data = []
        for order in orders:
            items = []
            for item in order.items:
                product = item.variation.product
                items.append({
                    "order_item_id": item.order_item_id,
                    "product_id": product.product_id,
                    "model": product.model,
                    "quantity": item.quantity,
                    "price": item.price,
                    "variation": f"{item.variation.color} {item.variation.year}"
                })
            order_data.append({
                "order_id": order.order_id,
                "order_date": order.order_date,
                "total_price": order.total_price,
                "status": order.status,
                "items": items
            })

    return render_template("customerAccount.html", user=user, orders=order_data)


@customer_account_bp.route("customer/review", methods=["POST"])
def submit_review():
    if not session or session.get("role") != "customer":
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    product_id = request.form.get("product_id", type=int)
    rating = request.form.get("rating", type=int)
    description = request.form.get("description")

    if not product_id or not rating or rating < 1 or rating > 5:
        flash("Invalid review data.", "error")
        return redirect(url_for("customer_account.customer_account"))

    with Session(engine) as session_db:
        # Check if user already reviewed this product
        existing = session_db.scalars(
            select(Review).where(Review.product_id == product_id, Review.customer_id == user_id)
        ).first()
        if existing:
            flash("You have already reviewed this product.", "error")
            return redirect(url_for("customer_account.customer_account"))

        review = Review(
            product_id=product_id,
            customer_id=user_id,
            rating=rating,
            description=description
        )
        session_db.add(review)
        session_db.commit()

    flash("Review submitted successfully.", "success")
    return redirect(url_for("customer_account.customer_account"))


@customer_account_bp.route("customer/complaint", methods=["POST"])
def submit_complaint():
    if not session or session.get("role") != "customer":
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    order_item_id = request.form.get("order_item_id", type=int)
    title = request.form.get("title")
    description = request.form.get("description")
    demand = request.form.get("demand")

    if not order_item_id or not title or demand not in ["return", "refund", "warranty_claim"]:
        flash("Invalid complaint data.", "error")
        return redirect(url_for("customer_account.customer_account"))

    with Session(engine) as session_db:
        # Check if order_item belongs to user
        order_item = session_db.get(OrderItem, order_item_id)
        if not order_item or order_item.order.customer_id != user_id:
            flash("Invalid order item.", "error")
            return redirect(url_for("customer_account.customer_account"))

        # Check if already complained about this item
        existing = session_db.scalars(
            select(Complaint).where(Complaint.order_item_id == order_item_id)
        ).first()
        if existing:
            flash("A complaint already exists for this item.", "error")
            return redirect(url_for("customer_account.customer_account"))

        complaint = Complaint(
            customer_id=user_id,
            order_item_id=order_item_id,
            title=title,
            description=description,
            demand=demand
        )
        session_db.add(complaint)
        session_db.commit()

    flash("Complaint submitted successfully.", "success")
    return redirect(url_for("customer_account.customer_account"))
