from flask import Blueprint, request, jsonify, redirect, url_for, flash, session
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db
from app.models import order
from app.models.order import Order, OrderStatus
from app.utils.payments import (create_stripe_payment_intent,
                                 create_paypal_payment, execute_paypal_payment)
import os
from app.extensions import csrf

payments_bp = Blueprint("payments", __name__)


def get_user():
    try:
        verify_jwt_in_request(locations=["cookies"])
        return get_current_user()
    except Exception:
        from flask import session as flask_session
        from app.models.user import User
        user_id = flask_session.get("user_id")
        if user_id:
            return User.query.get(user_id)
        return None


# ─── Stripe ──────────────────────────────────────────────────
@payments_bp.route("/stripe/create/<int:order_id>", methods=["POST"])
@csrf.exempt
def stripe_create(order_id):
    me = get_user()
    if not me:
        return jsonify({"error": "No autenticado"}), 401

    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()

    if order.payment_status == "paid":
        return jsonify({"error": "Este pedido ya fue pagado"}), 400

    intent = create_stripe_payment_intent(float(order.total))
    order.payment_id     = intent["id"]
    order.payment_method = "stripe"
    db.session.commit()

    return jsonify({
        "client_secret":  intent["client_secret"],
        "stripe_pub_key": os.getenv("STRIPE_PUBLIC_KEY"),
        "order_id":       order.id,
        "total":          float(order.total),
    })


@payments_bp.route("/stripe/confirm/<int:order_id>", methods=["POST"])
@csrf.exempt
def stripe_confirm(order_id):
    me = get_user()
    if not me:
        return jsonify({"error": "No autenticado"}), 401

    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()
    data  = request.get_json()

    if data.get("status") == "succeeded":
        order.payment_status = "paid"
        order.status         = OrderStatus.CONFIRMED
        db.session.commit()
        return jsonify({"success": True, "redirect": url_for("client.order_detail", order_id=order.id)})

    order.payment_status = "failed"
    db.session.commit()
    return jsonify({"success": False}), 400


# ─── PayPal ──────────────────────────────────────────────────
@payments_bp.route("/paypal/create/<int:order_id>")
@csrf.exempt
def paypal_create(order_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()

    if order.payment_status == "paid":
        flash("Este pedido ya fue pagado.", "warning")
        return redirect(url_for("client.order_detail", order_id=order.id))

    return_url = url_for("payments.paypal_execute", order_id=order.id, _external=True)
    cancel_url = url_for("client.order_detail",     order_id=order.id, _external=True)

    payment_id, approval_url = create_paypal_payment(
        float(order.total), return_url, cancel_url
    )

    if approval_url:
        order.payment_id     = payment_id
        order.payment_method = "paypal"
        db.session.commit()
        return redirect(approval_url)

    flash("Error al crear el pago con PayPal.", "danger")
    return redirect(url_for("client.order_detail", order_id=order.id))


@payments_bp.route("/paypal/execute")
@csrf.exempt
def paypal_execute():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    order    = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()
    payer_id = request.args.get("PayerID")

    if execute_paypal_payment(order.payment_id, payer_id):
        order.payment_status = "paid"
        order.status         = OrderStatus.CONFIRMED
        db.session.commit()
        flash(f"✅ Pago con PayPal confirmado. Pedido #{order.id} pagado.", "success")
    else:
        order.payment_status = "failed"
        db.session.commit()
        flash("❌ Error al procesar el pago con PayPal.", "danger")

    return redirect(url_for("client.order_detail", order_id=order.id))


@payments_bp.route("/paypal/cancel/<int:order_id>")
def paypal_cancel(order_id):
    flash("Pago con PayPal cancelado.", "warning")
    return redirect(url_for("client.order_detail", order_id=order.id))