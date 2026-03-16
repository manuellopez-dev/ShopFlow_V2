from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("main/index.html")

@main_bp.route("/docs/api")
def api_docs():
    return render_template("docs/api.html")

@main_bp.route("/docs/database")
def db_docs():
    return render_template("docs/database.html")

@main_bp.route("/docs/manual")
def manual():
    return render_template("docs/manual.html")