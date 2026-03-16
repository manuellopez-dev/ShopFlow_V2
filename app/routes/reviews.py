from flask import Blueprint, redirect, url_for, request, flash, session
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db
from app.models.product import Review, Favorite
from app.utils.sanitize import sanitize

reviews_bp = Blueprint("reviews", __name__)


def get_user():
    try:
        verify_jwt_in_request(locations=["cookies"])
        return get_current_user()
    except Exception:
        from app.models.user import User
        user_id = session.get("user_id")
        if user_id:
            return User.query.get(user_id)
        return None


@reviews_bp.route("/review/<int:product_id>", methods=["POST"])
def add_review(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    rating  = int(request.form.get("rating", 5))
    comment = sanitize(request.form.get("comment", "").strip())

    # Un usuario solo puede reseñar una vez por producto
    existing = Review.query.filter_by(product_id=product_id, user_id=me.id).first()
    if existing:
        flash("Ya escribiste una reseña para este producto.", "warning")
        return redirect(request.referrer or url_for("client.catalog"))

    if not 1 <= rating <= 5:
        flash("Calificación inválida.", "danger")
        return redirect(request.referrer or url_for("client.catalog"))

    review = Review(product_id=product_id, user_id=me.id,
                    rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    flash("¡Reseña publicada!", "success")
    return redirect(request.referrer or url_for("client.catalog"))


@reviews_bp.route("/favorite/<int:product_id>")
def toggle_favorite(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    existing = Favorite.query.filter_by(user_id=me.id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Eliminado de favoritos.", "info")
    else:
        fav = Favorite(user_id=me.id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        flash("¡Agregado a favoritos! ❤️", "success")

    return redirect(request.referrer or url_for("client.catalog"))


@reviews_bp.route("/favorites")
def my_favorites():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    from flask import render_template
    from app.models.product import Favorite
    favs = Favorite.query.filter_by(user_id=me.id).all()
    products = [f.product for f in favs if f.product.is_active]
    return render_template("client/favorites.html", products=products)