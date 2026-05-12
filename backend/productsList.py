import os
from flask import Blueprint, render_template, request, session, url_for
from math import ceil
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from .models import Product, engine

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
ALLOWED_CAR_TYPES = {"supercar", "classic", "motorcycle"}
IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "images", "products")
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)

productList_bp = Blueprint("productList", __name__, url_prefix="/products")

PRODUCT_IMAGES = {
    "Apex S Touring": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1800&q=85",
    "Apex X Performance": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1800&q=85",
    "Velora Hybrid LX": "https://images.unsplash.com/photo-1549924231-f129b911e442?auto=format&fit=crop&w=1800&q=85",
    "Velora EV Grand": "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1800&q=85",
}


@productList_bp.route("/", methods=["GET"])
@productList_bp.route("/<int:page>", methods=["GET"])
def products(page=1):
    model_filter = request.args.get("model_filter", "").strip()
    car_type_filter = request.args.get("car_type", "").strip()
    if car_type_filter not in ALLOWED_CAR_TYPES:
        car_type_filter = ""

    page = int(page)
    if page < 1:
        page = 1

    per_page = 10

    with Session(engine) as session_db:
        base_query = select(Product).options(
            selectinload(Product.vendor),
            selectinload(Product.images),
            selectinload(Product.variations),
        )

        if model_filter:
            base_query = base_query.where(Product.model.ilike(f"%{model_filter}%"))

        if car_type_filter:
            base_query = base_query.where(Product.carType == car_type_filter)

        total_products = len(session_db.scalars(
            base_query.with_only_columns(Product.product_id)
        ).all())

        total_pages = max(1, ceil(total_products / per_page))
        if page > total_pages:
            page = total_pages

        products_list = session_db.scalars(
            base_query
            .order_by(Product.product_id.asc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).all()

    for product in products_list:
        product.display_image_url = PRODUCT_IMAGES.get(product.model)
        for ext in ALLOWED_IMAGE_EXTENSIONS:
            filename = f"product_{product.product_id}.{ext}"
            filepath = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                product.display_image_url = url_for("static", filename=f"images/products/{filename}")
                product.display_image_url += f"?v={int(os.path.getmtime(filepath))}"
                break

    return render_template(
        "products.html",
        products=products_list,
        session=session,
        page=page,
        per_page=per_page,
        count=total_products,
        total_pages=total_pages,
        model_filter=model_filter,
        car_type_filter=car_type_filter,
    )
