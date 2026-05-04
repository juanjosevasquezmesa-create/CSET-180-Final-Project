# Demo checkout route: shows cart and payment form

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .models import CartItem, ProductVariation, Order, OrderItem, engine

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout/")

@checkout_bp.route("", methods=["GET", "POST"])
def checkout():
	if "user_id" not in session:
		return redirect(url_for("login.login"))
	if session.get("role") != "customer":
		flash("Only customer accounts can checkout.", "error")
		return redirect(url_for("index.index"))

	user_id = session["user_id"]
	payment_success = False
	cart_items = []
	cart_total = 0

	with Session(engine) as session_db:
		db_cart_items = session_db.scalars(
			select(CartItem)
			.where(CartItem.customer_id == user_id)
			.options(selectinload(CartItem.variation).selectinload(ProductVariation.product))
		).all()

		for item in db_cart_items:
			if not item.variation or not item.variation.product:
				session_db.delete(item)
				continue
			cart_items.append({
				"product_name": item.variation.product.model,
				"quantity": item.quantity,
				"price": float(item.variation.product.price),
				"color": item.variation.color,
				"year": item.variation.year,
			})
			cart_total += float(item.variation.product.price) * item.quantity
		session_db.commit()

		if request.method == "POST":
			# Payment form submitted, create order and clear cart
			if not cart_items:
				flash("Your cart is empty.", "error")
				return redirect(url_for("cartPage.view_cart"))

			order = Order(customer_id=user_id, total_price=cart_total, status="pending")
			session_db.add(order)
			session_db.flush()
			for item in db_cart_items:
				if not item.variation or not item.variation.product:
					continue
				order_item = OrderItem(
					order_id=order.order_id,
					var_id=item.var_id,
					quantity=item.quantity,
					price=float(item.variation.product.price)
				)
				session_db.add(order_item)
				item.variation.stock -= item.quantity
				session_db.delete(item)
			session_db.commit()
			payment_success = True
			return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total, payment_success=payment_success)

	return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total, payment_success=payment_success)