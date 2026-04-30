from flask import Blueprint, render_template, session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from .models import Product, engine


productList_bp = Blueprint("productList", __name__, url_prefix="/products")


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

    return render_template("products.html", products=products, session=session)
