from flask import Blueprint, render_template, session


index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    name = session.get("name") if session.get("user_id") else None
    first_name = name.split(" ", 1)[0] if name else None
    return render_template("index.html", session=session, name=first_name)
