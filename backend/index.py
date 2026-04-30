from flask import Blueprint, render_template, session


index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    if session:
        name = session.get("name")
        nameList = name.split()
    return render_template("index.html", session=session)
