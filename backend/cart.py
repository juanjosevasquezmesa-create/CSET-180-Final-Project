from flask import Blueprint, session, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CartItem, Product, ProductVariation, engine

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.route("/items", methods=["GET"])
def get_cart_items():
    """Fetch all cart items for the logged-in customer (view-only)"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

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
            product = session_db.get(Product, item.variation.product_id)
            variation = item.variation
            
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
                "item_total": item_total,
            })
        
        return jsonify({
            "items": items_data,
            "total_price": total_price,
            "item_count": len(items_data)
        })
