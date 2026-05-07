import os
from flask import Blueprint, render_template, request, session, url_for
from math import ceil
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from .models import Product, engine

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "images", "products")
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)

productList_bp = Blueprint("productList", __name__, url_prefix="/products")

PRODUCT_IMAGES = {
    "Apex S Touring":      "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1800&q=85",
    "Apex X Performance":  "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1800&q=85",
    "Velora Hybrid LX":    "https://images.unsplash.com/photo-1549924231-f129b911e442?auto=format&fit=crop&w=1800&q=85",
    "Velora EV Grand":     "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1800&q=85",
}


@productList_bp.route("/", methods=["GET"])
@productList_bp.route("/<int:page>", methods=["GET"])
def products(page=1):

    # ── Read query-string params ──────────────────────────────────────────
    sort_by      = request.args.get("sort_by",      "product_id")
    sort_dir     = request.args.get("sort_dir",     "asc")
    model_filter = request.args.get("model_filter", "")

    # ── Whitelist sort columns / directions ───────────────────────────────
    allowed_sort_columns = {
        "product_id":      Product.product_id,
        "model":           Product.model,
        "warranty_period": Product.warranty_period,
    }
    if sort_by  not in allowed_sort_columns: sort_by  = "product_id"
    if sort_dir not in {"asc", "desc"}:      sort_dir = "asc"

    sort_col = allowed_sort_columns[sort_by]
    sort_col = sort_col.asc() if sort_dir == "asc" else sort_col.desc()

    page = int(page)
    if page < 1:
        page = 1

    per_page = 10

    with Session(engine) as session_db:

        # ── Base query with filters ───────────────────────────────────────
        base_query = select(Product).options(
            selectinload(Product.vendor),
            selectinload(Product.images),
            selectinload(Product.variations),
        )

        if model_filter:
            base_query = base_query.where(Product.model.ilike(f"%{model_filter}%"))

        # ── Price bounds for sliders ──────────────────────────────────────
        all_prices = session_db.scalars(select(Product.price)).all()
        price_min_bound = float(min(all_prices)) if all_prices else 0
        price_max_bound = float(max(all_prices)) + 1 if all_prices else 1

        # ── Total count for pagination ────────────────────────────────────
        total_products = session_db.scalar(
            select(Product.product_id).where(
                *([Product.model.ilike(f"%{model_filter}%")] if model_filter else []),
            ).with_only_columns(Product.product_id)
        )
        # simpler: just count from the filtered result
        total_products = len(session_db.scalars(
            base_query.with_only_columns(Product.product_id)
        ).all())

        total_pages = max(1, ceil(total_products / per_page))
        if page > total_pages:
            page = total_pages

        # ── Paginated + sorted fetch ──────────────────────────────────────
        products_list = session_db.scalars(
            base_query
            .order_by(sort_col)
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).all()

    # ── Attach display image (same logic as original) ─────────────────────
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
        sort_by=sort_by,
        sort_dir=sort_dir,
        model_filter=model_filter,
        price_min_bound=price_min_bound,
        price_max_bound=price_max_bound,
    )