from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db
from app.models.order import Coupon
from app.extensions import csrf

coupons_bp = Blueprint("coupons", __name__)


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


# ─── Admin: gestión de cupones ────────────────────────
@coupons_bp.route("/admin/coupons")
def list_coupons():
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template("admin/coupons.html", coupons=coupons)


@coupons_bp.route("/admin/coupons/create", methods=["GET", "POST"])
def create_coupon():
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        code           = request.form.get("code", "").strip().upper()
        discount_type  = request.form.get("discount_type", "percent")
        discount_value = float(request.form.get("discount_value", 0))
        min_order      = float(request.form.get("min_order", 0))
        max_uses       = int(request.form.get("max_uses", 100))
        expires_at     = request.form.get("expires_at") or None

        if Coupon.query.filter_by(code=code).first():
            flash("Ese código ya existe.", "warning")
            return render_template("admin/coupon_form.html")

        from datetime import datetime
        coupon = Coupon(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order=min_order,
            max_uses=max_uses,
            expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        )
        db.session.add(coupon)
        db.session.commit()
        flash(f"Cupón '{code}' creado.", "success")
        return redirect(url_for("coupons.list_coupons"))

    return render_template("admin/coupon_form.html")


@coupons_bp.route("/admin/coupons/<int:coupon_id>/toggle")
def toggle_coupon(coupon_id):
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))
    coupon = Coupon.query.get_or_404(coupon_id)
    coupon.is_active = not coupon.is_active
    db.session.commit()
    flash(f"Cupón {'activado' if coupon.is_active else 'desactivado'}.", "info")
    return redirect(url_for("coupons.list_coupons"))


# ─── Cliente: aplicar cupón ───────────────────────────
@coupons_bp.route("/apply", methods=["POST"])
@csrf.exempt
def apply_coupon():
    code  = request.form.get("coupon_code", "").strip().upper()
    cart  = session.get("cart", {})

    if not cart:
        return jsonify({"error": "Carrito vacío"}), 400

    from app.models.product import Product
    subtotal = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal += float(product.price) * qty

    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify({"error": "Cupón no encontrado"}), 404

    valid, msg = coupon.is_valid(subtotal)
    if not valid:
        return jsonify({"error": msg}), 400

    new_total = coupon.apply(subtotal)
    discount  = round(subtotal - new_total, 2)

    session["coupon_code"]    = code
    session["coupon_discount"] = discount

    return jsonify({
        "success":   True,
        "code":      code,
        "subtotal":  subtotal,
        "discount":  discount,
        "new_total": new_total,
        "message":   f"¡Cupón aplicado! Descuento: ${discount:.2f}"
    })
    