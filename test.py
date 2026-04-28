from flask import Blueprint, render_template, redirect, request, url_for
from sqlalchemy import or_, select, distinct
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from backend.models import User, Product, engine




def testFunction():

    with Session(engine) as session_db:
        # existing_user = session_db.scalars(
        #     select(distinct(User.name)).where(User.user_id == Product.vendor_id)  
        # ).all()
        existing_user = session_db.scalars(
            select(User, Product).join(Product, User.user_id == Product.vendor_id)  
        ).all()
        
        products = session_db.scalars(
            select(User, Product).join(Product, User.user_id == Product.vendor_id)  
        ).all()
        
        
        # for user in products:
        #     print(user)

    return print("signup.html")

testFunction()