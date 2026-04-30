from flask import Blueprint, render_template, session


index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    nameList = []
    if session:
        name = session.get("name")
        nameList = name.split(" ", 1)
    return render_template("index.html", session=session, name= nameList[0] if nameList else None)
