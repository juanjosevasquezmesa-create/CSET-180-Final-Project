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
from backend.vendorAccount import vendor_Account_bp
from backend.vendorAdd import productAdd_bp
from backend.vendorDelete import productDel_bp
from backend.vendorEdit import productEdit_bp
from backend.vendorProduct import vendorProduct_bp

app = Flask(__name__)
# Now you can access variables like this:
# app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
#same as app.secret_key = string

app.permanent_session_lifetime = timedelta(days=7)# It enables session persistence beyond closing the browser, with a default lifespan of 31 days. If inactive, the session cookie expires, forcing user re-authentication.

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
app.register_blueprint(vAccount_bp)
# app.register_blueprint(productAdd_bp)
# app.register_blueprint(productDel_bp)
# app.register_blueprint(productEdit_bp)
app.register_blueprint(vendorProduct_bp)
if __name__ == "__main__":
    app.run(debug=True)

