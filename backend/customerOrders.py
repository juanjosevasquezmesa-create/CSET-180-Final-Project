# functionality for customer review, complaints, and order details in account page

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, Order, OrderItem, Review, Complaint, engine

customer_orders_bp = Blueprint("customer_orders", __name__, url_prefix="/account/")


@customer_orders_bp.route("customer/order/<int:order_id>", methods=["GET"])
def order_details(order_id):
    if not session or session.get("role") != "customer":
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    with Session(engine) as session_db:
        order = session_db.get(Order, order_id)
        if not order or order.customer_id != user_id:
            return redirect(url_for("customer_account.customer_account"))

        items = []
        for item in order.items:
            product = item.variation.product
            items.append({
                "order_item_id": item.order_item_id,
                "product_id": product.product_id,
                "model": product.model,
                "quantity": item.quantity,
                "price": item.price,
                "line_total": float(item.price) * item.quantity,
                "variation": f"{item.variation.color} {item.variation.year}"
            })

        order_data = {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "total_price": order.total_price,
            "status": order.status,
            "items": items,
        }

    return render_template("customerOrderDetails.html", order=order_data)


@customer_orders_bp.route("customer/review", methods=["POST"])
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
            description=description,
        )
        session_db.add(review)
        session_db.commit()

    flash("Review submitted successfully.", "success")
    return redirect(url_for("customer_account.customer_account"))


@customer_orders_bp.route("customer/complaint", methods=["POST"])
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
        order_item = session_db.get(OrderItem, order_item_id)
        if not order_item or order_item.order.customer_id != user_id:
            flash("Invalid order item.", "error")
            return redirect(url_for("customer_account.customer_account"))

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
            demand=demand,
        )
        session_db.add(complaint)
        session_db.commit()

    flash("Complaint submitted successfully.", "success")
    return redirect(url_for("customer_account.customer_account"))
