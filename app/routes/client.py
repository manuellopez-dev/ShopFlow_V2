import os

from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, session)
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.category import Category
from app.utils.sanitize import sanitize
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, session, jsonify)

from app.utils.stock_monitor import check_low_stock
from app.models.user import User

client_bp = Blueprint("client", __name__)


def get_user():
    from flask import session as flask_session
    from app.models.user import User
    try:
        verify_jwt_in_request(locations=["cookies"])
        return get_current_user()
    except Exception:
        user_id = flask_session.get("user_id")
        if user_id:
            return User.query.get(user_id)
        return None


@client_bp.route("/catalog")
def catalog():
    category_id = request.args.get("category", type=int)
    search      = request.args.get("q", "").strip()
    sort        = request.args.get("sort", "newest")
    min_price   = request.args.get("min_price", type=float)
    max_price   = request.args.get("max_price", type=float)

    query = Product.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products   = query.all()
    categories = Category.query.filter_by(is_active=True).all()
    total_products = len(products)

    return render_template("client/catalog.html",
        products=products,
        categories=categories,
        selected_cat=category_id,
        search=search,
        sort=sort,
        min_price=min_price or "",
        max_price=max_price or "",
        total_products=total_products,
    )


@client_bp.route("/cart")
def cart():
    cart  = session.get("cart", {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product and product.is_active:
            subtotal = float(product.price) * qty
            total   += subtotal
            items.append({"product": product, "qty": qty, "subtotal": subtotal})
    return render_template("client/cart.html", items=items, total=total)


@client_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty     = int(request.form.get("qty", 1))
    cart    = session.get("cart", {})
    key     = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    session["cart"] = cart

    cart_count = sum(cart.values())

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success":    True,
            "message":    f"'{product.name}' agregado al carrito.",
            "cart_count": cart_count
        })

    flash(f"'{product.name}' agregado al carrito.", "success")
    return redirect(url_for("client.catalog"))


@client_bp.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("client.cart"))


@client_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    cart = session.get("cart", {})
    if not cart:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("client.catalog"))

    if request.method == "POST":
        from app.models.order import Coupon
        coupon_code = request.form.get("coupon_code", "").strip().upper() or None
        coupon      = Coupon.query.filter_by(code=coupon_code).first() if coupon_code else None

        order = Order(client_id=me.id, status=OrderStatus.PENDING)
        db.session.add(order)

        for pid, qty in cart.items():
            product = Product.query.get(int(pid))
            if product and product.stock >= qty:
                unit_price = product.get_discounted_price(qty)
                item = OrderItem(order=order, product_id=product.id,
                                quantity=qty, unit_price=unit_price)
                product.stock -= qty
                db.session.add(item)

                # Verificar stock bajo
                if product.stock <= product.min_stock:
                    vendor = User.query.get(product.vendor_id)
                    if vendor:
                        check_low_stock(product, vendor)

        order.calculate_total()

        if coupon:
            valid, _ = coupon.is_valid(float(order.total))
            if valid:
                new_total = coupon.apply(float(order.total))
                order.discount    = float(order.total) - new_total
                order.coupon_code = coupon_code
                order.total       = new_total
                coupon.used_count += 1

        db.session.commit()
        db.session.commit()

        # ─── Notificar a vendors ──────────────────────
        try:
            from app.utils.email import send_vendor_sale_email
            vendors_notified = set()
            for item in order.items:
                vendor = item.product.vendor
                if vendor and vendor.id not in vendors_notified:
                    send_vendor_sale_email(vendor, order)
                    vendors_notified.add(vendor.id)
        except Exception as e:
            print(f"[EMAIL VENDOR] {e}")

        session.pop("cart", None)
        session.pop("coupon_code", None)
        session.pop("coupon_discount", None)
        flash(f"Pedido #{order.id} confirmado. ¡Completa tu pago!", "success")
        return redirect(url_for("client.shipping", order_id=order.id))

    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = float(product.price) * qty
            total   += subtotal
            items.append({"product": product, "qty": qty, "subtotal": subtotal})
    return render_template("client/checkout.html", items=items, total=total)


@client_bp.route("/orders")
def my_orders():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    page   = request.args.get("page", 1, type=int)
    orders = Order.query.filter_by(client_id=me.id)\
                  .order_by(Order.created_at.desc())\
                  .paginate(page=page, per_page=10)
    return render_template("client/orders.html", orders=orders)


@client_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()
    return render_template("client/order_detail.html", order=order)

@client_bp.route("/orders/<int:order_id>/payment")
def payment(order_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()
    return render_template("client/payment.html",
                           order=order,
                           stripe_pub_key=os.getenv("STRIPE_PUBLIC_KEY"))

@client_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    from app.models.product import Review
    product  = Product.query.get_or_404(product_id)
    reviews  = Review.query.filter_by(product_id=product_id)\
                 .order_by(Review.created_at.desc()).all()
    related  = product.get_related(limit=4)
    me       = get_user()
    user_reviewed = False
    if me:
        user_reviewed = Review.query.filter_by(
            product_id=product_id, user_id=me.id).first() is not None
    return render_template("client/product_detail.html",
                           product=product, reviews=reviews,
                           user_reviewed=user_reviewed, related=related)

@client_bp.route("/profile", methods=["GET", "POST"])
def profile():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        from app.extensions import bcrypt
        action = request.form.get("action")

        if action == "update_info":
            name  = sanitize(request.form.get("name", "").strip())
            email = sanitize(request.form.get("email", "").strip())
            from app.models.user import User
            existing = User.query.filter(User.email == email, User.id != me.id).first()
            if existing:
                flash("Ese email ya está en uso.", "danger")
            elif not name or not email:
                flash("Nombre y email son requeridos.", "danger")
            else:
                me.name  = name
                me.email = email
                db.session.commit()
                flash("Perfil actualizado correctamente.", "success")

        elif action == "change_password":
            current  = request.form.get("current_password", "")
            new_pass = request.form.get("new_password", "")
            confirm  = request.form.get("confirm_password", "")

            if not bcrypt.check_password_hash(me.password_hash, current):
                flash("Contraseña actual incorrecta.", "danger")
            elif len(new_pass) < 8:
                flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
            elif new_pass != confirm:
                flash("Las contraseñas no coinciden.", "danger")
            else:
                me.password_hash = bcrypt.generate_password_hash(new_pass).decode("utf-8")
                db.session.commit()
                flash("Contraseña actualizada correctamente.", "success")

        return redirect(url_for("client.profile"))

    # Stats del usuario
    total_orders    = Order.query.filter_by(client_id=me.id).count()
    delivered       = Order.query.filter_by(client_id=me.id, status="delivered").count()
    total_spent     = db.session.query(db.func.sum(Order.total)).filter_by(
                        client_id=me.id, payment_status="paid").scalar() or 0
    from app.models.product import Review, Favorite
    total_reviews   = Review.query.filter_by(user_id=me.id).count()
    total_favorites = Favorite.query.filter_by(user_id=me.id).count()

    return render_template("client/profile.html",
        me=me,
        total_orders=total_orders,
        delivered=delivered,
        total_spent=total_spent,
        total_reviews=total_reviews,
        total_favorites=total_favorites,
    )

@client_bp.route("/orders/<int:order_id>/shipping", methods=["GET", "POST"])
def shipping(order_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    order = Order.query.filter_by(id=order_id, client_id=me.id).first_or_404()

    if request.method == "POST":
        order.shipping_address = request.form.get("address", "").strip()
        order.shipping_city    = request.form.get("city", "").strip()
        order.shipping_state   = request.form.get("state", "").strip()
        order.shipping_zip     = request.form.get("zip_code", "").strip()
        order.shipping_phone   = request.form.get("phone", "").strip()

        if not all([order.shipping_address, order.shipping_city,
                    order.shipping_state, order.shipping_phone]):
            flash("Por favor completa todos los campos requeridos.", "danger")
            return render_template("client/shipping.html", order=order)

        db.session.commit()
        flash("Dirección guardada. ¡Completa tu pago!", "success")
        return redirect(url_for("client.payment", order_id=order.id))

    return render_template("client/shipping.html", order=order)