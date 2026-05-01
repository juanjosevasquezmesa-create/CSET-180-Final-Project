from flask import Blueprint, render_template, session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from .models import Product, engine


productList_bp = Blueprint("productList", __name__, url_prefix="/products")

PRODUCT_IMAGES = {
    "Apex S Touring": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1800&q=85",
    "Apex X Performance": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1800&q=85",
    "Velora Hybrid LX": "https://images.unsplash.com/photo-1549924231-f129b911e442?auto=format&fit=crop&w=1800&q=85",
    "Velora EV Grand": "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1800&q=85",
}


@productList_bp.route("/", methods=["GET"])
def products():
    with Session(engine) as session_db:
        products = session_db.scalars(
            select(Product)
            .options(
                selectinload(Product.vendor),
                selectinload(Product.images),
                selectinload(Product.variations),
            )
            .order_by(Product.product_id)
        ).all()

    for product in products:
        product.display_image_url = PRODUCT_IMAGES.get(product.model)

    return render_template("products.html", products=products, session=session)
