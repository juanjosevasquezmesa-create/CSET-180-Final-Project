from flask import Blueprint, request, session, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CartItem, ProductVariation, engine

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.route("/add", methods=["POST"])
def add_cart_item():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "customer":
        return jsonify({"error": "Only customer accounts can use the cart."}), 403

    data = request.get_json(silent=True) or {}
    variation_id = data.get("variation_id")

    if not variation_id:
        return jsonify({"error": "Missing product option."}), 400

    user_id = session["user_id"]

    with Session(engine) as session_db:
        variation = session_db.get(ProductVariation, variation_id)

        if not variation:
            return jsonify({"error": "Product option not found."}), 404

        if not variation.product:
            return jsonify({"error": "This product is no longer available."}), 404

        if variation.stock < 1:
            return jsonify({"error": "This option is out of stock."}), 400

        cart_item = session_db.scalars(
            select(CartItem).where(
                CartItem.customer_id == user_id,
                CartItem.var_id == variation.var_id,
            )
        ).first()

        if cart_item:
            if cart_item.quantity >= variation.stock:
                return jsonify({"error": "No more stock available for this option."}), 400
            cart_item.quantity += 1
        else:
            session_db.add(
                CartItem(
                    customer_id=user_id,
                    var_id=variation.var_id,
                    quantity=1,
                )
            )

        session_db.commit()

    return jsonify({"success": True})


@cart_bp.route("/items/<int:cart_item_id>", methods=["PATCH"])
def update_cart_item(cart_item_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "customer":
        return jsonify({"error": "Only customer accounts can use the cart."}), 403

    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity must be a number."}), 400

    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1."}), 400

    with Session(engine) as session_db:
        cart_item = session_db.get(CartItem, cart_item_id)

        if not cart_item or cart_item.customer_id != session["user_id"]:
            return jsonify({"error": "Cart item not found."}), 404

        if not cart_item.variation.product:
            session_db.delete(cart_item)
            session_db.commit()
            return jsonify({"error": "This product is no longer available."}), 404

        if quantity > cart_item.variation.stock:
            return jsonify({"error": "Quantity exceeds available stock."}), 400

        cart_item.quantity = quantity
        session_db.commit()

    return jsonify({"success": True})


@cart_bp.route("/items/<int:cart_item_id>", methods=["DELETE"])
def remove_cart_item(cart_item_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "customer":
        return jsonify({"error": "Only customer accounts can use the cart."}), 403

    with Session(engine) as session_db:
        cart_item = session_db.get(CartItem, cart_item_id)

        if not cart_item or cart_item.customer_id != session["user_id"]:
            return jsonify({"error": "Cart item not found."}), 404

        session_db.delete(cart_item)
        session_db.commit()

    return jsonify({"success": True})


@cart_bp.route("/items", methods=["GET"])
def get_cart_items():
    """Fetch all cart items for the logged-in customer (view-only)"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "customer":
        return jsonify({"error": "Only customer accounts can use the cart."}), 403

    user_id = session["user_id"]
    
    with Session(engine) as session_db:
        # Fetch all cart items for this customer with product details
        cart_items = session_db.scalars(
            select(CartItem).where(CartItem.customer_id == user_id)
        ).all()
        
        items_data = []
        total_price = 0
        
        for item in cart_items:
            # Get product and variation details
            variation = item.variation
            product = variation.product

            if not product:
                session_db.delete(item)
                continue
            
            item_total = float(product.price) * item.quantity
            total_price += item_total
            
            items_data.append({
                "cart_item_id": item.cart_item_id,
                "product_id": product.product_id,
                "model": product.model,
                "color": variation.color,
                "year": variation.year,
                "price": float(product.price),
                "quantity": item.quantity,
                "stock": variation.stock,
                "item_total": item_total,
            })
        session_db.commit()

        return jsonify({
            "items": items_data,
            "total_price": total_price,
            "item_count": len(items_data)
        })
