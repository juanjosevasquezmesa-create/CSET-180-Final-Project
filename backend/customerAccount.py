# Hub for customer account functions

from flask import Blueprint, render_template, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, Order, engine
from .customerOrders import order_item_data

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

        orders = session_db.scalars(
            select(Order).where(Order.customer_id == user_id).order_by(Order.order_date.desc())
        ).all()

        order_data = []
        for order in orders:
            items = []
            for item in order.items:
                items.append(order_item_data(item))
            order_data.append({
                "order_id": order.order_id,
                "order_date": order.order_date,
                "total_price": order.total_price,
                "status": order.status,
                "items": items,
                "detail_url": url_for("customer_orders.order_details", order_id=order.order_id),
            })

    return render_template("customerAccount.html", user=user, orders=order_data)
