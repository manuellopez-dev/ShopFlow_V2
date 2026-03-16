from app.utils import sanitize
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db, bcrypt
from app.models.user import User, Role
from app.models.product import Product
from app.models.order import Order
from app.models.category import Category

admin_bp = Blueprint("admin", __name__)

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

@admin_bp.route("/dashboard")
def dashboard():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    from app.models.order import Order, OrderStatus
    from sqlalchemy import func
    import json

    stats = {
        "users":    User.query.count(),
        "products": Product.query.filter_by(is_active=True).count(),
        "orders":   Order.query.count(),
        "vendors":  User.query.filter_by(role=Role.VENDOR).count(),
        "revenue":  db.session.query(func.sum(Order.total)).filter_by(payment_status="paid").scalar() or 0,
    }

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    # ─── Pedidos por estado ───────────────────────────
    status_data = {}
    for s in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED,
              OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        status_data[s] = Order.query.filter_by(status=s).count()

    # ─── Ingresos últimos 7 días ──────────────────────
    from datetime import datetime, timedelta, timezone
    today     = datetime.now(timezone.utc).date()
    days      = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    revenue_by_day = []
    for day in days:
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end   = start + timedelta(days=1)
        total = db.session.query(func.sum(Order.total)).filter(
            Order.created_at >= start,
            Order.created_at < end,
            Order.payment_status == "paid"
        ).scalar() or 0
        revenue_by_day.append(float(total))

    day_labels = [d.strftime('%d/%m') for d in days]

    # ─── Productos más vendidos ───────────────────────
    from app.models.order import OrderItem
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(OrderItem).group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(5).all()

    top_names  = [p.name for p in top_products]
    top_sales  = [int(p.total_sold) for p in top_products]

    return render_template("admin/dashboard.html",
        stats=stats,
        recent_orders=recent_orders,
        status_data=json.dumps(status_data),
        day_labels=json.dumps(day_labels),
        revenue_by_day=json.dumps(revenue_by_day),
        top_names=json.dumps(top_names),
        top_sales=json.dumps(top_sales),
    )


@admin_bp.route("/users")
def users():
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))
    page  = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        name = sanitize(request.form.get("name", "").strip())
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role     = request.form.get("role", Role.CLIENT)

        if role not in Role.ALL:
            flash("Rol inválido.", "danger")
            return render_template("admin/user_form.html", roles=Role.ALL)

        if User.query.filter_by(email=email).first():
            flash("El correo ya está en uso.", "warning")
            return render_template("admin/user_form.html", roles=Role.ALL)

        pw_hash = bcrypt.generate_password_hash(password, rounds=12).decode()
        user = User(name=name, email=email, password_hash=pw_hash, role=role)
        db.session.add(user)
        db.session.commit()
        flash(f"Usuario {name} creado.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", roles=Role.ALL, user=None)


@admin_bp.route("/users/<int:user_id>/toggle")
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    me   = get_current_user()
    if user.id == me.id:
        flash("No puedes desactivar tu propia cuenta.", "warning")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        state = "activado" if user.is_active else "desactivado"
        flash(f"Usuario {user.name} {state}.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/categories")
def categories():
    cats = Category.query.all()
    return render_template("admin/categories.html", categories=cats)


@admin_bp.route("/categories/create", methods=["GET", "POST"])
def create_category():
    if request.method == "POST":
        name = sanitize(request.form.get("name", "").strip())
        desc = request.form.get("description", "").strip()
        if not name:
            flash("El nombre es obligatorio.", "danger")
            return render_template("admin/category_form.html", category=None)
        cat = Category(name=name, description=desc)
        db.session.add(cat)
        db.session.commit()
        flash(f"Categoría '{name}' creada.", "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", category=None)


@admin_bp.route("/orders")
def orders():
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))
    from app.models.order import Order
    page   = request.args.get("page", 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template("admin/orders.html", orders=orders)

@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    me = get_user()
    if not me or not me.is_admin():
        return redirect(url_for("auth.login"))

    from app.models.order import Order
    from app.models.user import User
    from app.utils.email import send_order_status_email

    order  = Order.query.get_or_404(order_id)
    status = request.form.get("status")
    valid  = ["pending", "confirmed", "shipped", "delivered", "cancelled"]

    if status in valid:
        order.status = status
        db.session.commit()

        # Enviar email al cliente
        try:
            client = User.query.get(order.client_id)
            print(f"[EMAIL] Cliente: {client}, Order status: {order.status}")
            if client:
                send_order_status_email(client, order)
                print(f"[EMAIL] Enviado exitosamente a {client.email}")
        except Exception as e:
            import traceback
            traceback.print_exc()

        flash(f"Pedido #{order_id} actualizado a '{status}'. Email enviado.", "success")

    return redirect(url_for("admin.orders"))