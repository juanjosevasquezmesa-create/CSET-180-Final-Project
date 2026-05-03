from flask import Blueprint, render_template, redirect, request, url_for
from sqlalchemy import or_, select, distinct
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from backend.models import User, Product, ProductVariation, engine


def testFunction():

    with Session(engine) as session_db:
        # existing_user = session_db.scalars(
        #     select(distinct(User.name)).where(User.user_id == Product.vendor_id)  
        # ).all()
        existing_user = session_db.scalars(
            select(User, Product).join(Product, User.user_id == Product.vendor_id)  
        ).all()
        
        products = session_db.execute(
            select(Product, User, ProductVariation)
            .join(User, User.user_id == Product.vendor_id)
            .join(ProductVariation, ProductVariation.product_id == Product.product_id)
        ).all()
        
        
        
        for product, user, variation in products:
            print(product.__dict__)
            print(user.__dict__)
            print(variation.__dict__)
            print("-----")

    return print("signup.html")

# testFunction()

def testFunction2(user_id):
    with Session(engine) as session_db:
        user = session_db.get(User, user_id)
        
        if not user:
            pass #add some error saying that user not found
            # return redirect(url_for('all_accounts', error='User not found'))
        
        # Prevent admin from modifying their own verification status
        # if user.role == "admin" and session.get('userID') == user_id:
            pass #add some error saying admin cannot change their own accoutn
            # return redirect(url_for('all_accounts', error='Cannot modify your own verification status'))
        
        # Toggle verification status
        user.isVerified = "verified"
        
        session_db.commit()
        if user.isVerified == "verified":
            print(user.name, user.isVerified)
        # success_message = f"User {'verified' if user.isVerified else 'unverified'} successfully"
        return # redirect the admin to the all accounts page # redirect(url_for('all_accounts', success=success_message))
    
# testFunction2(7)

def allVendorAccounts():
    with Session(engine) as session_db:
        vendors = session_db.scalars(select(User).join(Product, User.user_id == Product.vendor_id).distinct()).all()
        # or vendor_users = session_db.query(User).join(Product, User.user_id == Product.vendor_id).distinct().all()
        
        for user in vendors:
            print(user.user_id)

# allVendorAccounts()

def getVendorName(product_id):
    with Session(engine) as session_db:
        productUser = session_db.scalars(select(User.user_id).join(Product, User.user_id == Product.vendor_id).where(Product.product_id == product_id)).first()
        
        print("Vendor id:",productUser)
        return ""
    

# getVendorName(2)

def showAllOrders(user_id):
    pass