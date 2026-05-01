from flask import Blueprint, render_template, session, redirect, url_for
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from .models import Product, User,  engine


productDel_bp = Blueprint("productDel", __name__, url_prefix="/account/vendor/")


@productDel_bp.route("<int:product_num>", methods=["POST"])
def productDel(product_id):
    with Session(engine) as session_db:
        productUser = session_db.scalars(select(User.user_id).join(Product, User.user_id == Product.vendor_id).where(Product.product_id == product_id)).first()
        
        if productUser != session.get("user_id"): # this makes 
            pass
            # flash error 
            # redirect to the main page
        productDelete = delete(Product).where(Product.product_id == product_id)
        session_db.execute(productDelete)
        session_db.commit()
        # flash success
        
        return redirect(url_for("vAccount.vendorAcc"))
