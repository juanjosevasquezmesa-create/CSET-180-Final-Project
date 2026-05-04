from flask import Flask
from datetime import timedelta

from backend.config import FLASK_SECRET_KEY
from backend.index import index_bp
from backend.login import login_bp
from backend.signup import signup_bp
from backend.logout import logout_bp
from backend.productsList import productList_bp
from backend.cart import cart_bp
from backend.cartPage import cart_page_bp
from backend.cartToOrder import cartToOrder_bp
from backend.chat import chat_bp
from backend.adminAccount import admin_account_bp
from backend.customerAccount import customer_account_bp
from backend.customerOrders import customer_orders_bp
from backend.vendorAccount import vendor_account_bp
from backend.vendorProduct import vendor_Product_bp
from backend.checkout import checkout_bp

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(days=7)

app.config["SECRET_KEY"] = FLASK_SECRET_KEY

app.register_blueprint(index_bp)
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(productList_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(cart_page_bp)
app.register_blueprint(cartToOrder_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(vendor_account_bp)
app.register_blueprint(vendor_Product_bp)
app.register_blueprint(customer_account_bp)
app.register_blueprint(customer_orders_bp)
app.register_blueprint(admin_account_bp)
app.register_blueprint(checkout_bp)

if __name__ == "__main__":
    app.run(debug=True)
