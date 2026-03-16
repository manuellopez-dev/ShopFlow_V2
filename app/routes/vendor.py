from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from app.extensions import db
from app.models.product import Product
from app.models.category import Category
import os
from werkzeug.utils import secure_filename
from app.utils.sanitize import sanitize, sanitize_html
from app.models.product import PriceHistory

vendor_bp = Blueprint("vendor", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
UPLOAD_FOLDER      = "app/static/uploads/products"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


@vendor_bp.route("/dashboard")
def dashboard():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))

    from app.models.order import Order, OrderItem
    from sqlalchemy import func
    import json

    # ─── Stats generales ─────────────────────────────
    my_products    = Product.query.filter_by(vendor_id=me.id, is_active=True).count()
    total_products = Product.query.filter_by(vendor_id=me.id).count()
    low_stock      = Product.query.filter(
                        Product.vendor_id == me.id,
                        Product.stock <= 5,
                        Product.is_active == True
                     ).count()

    # ─── Ventas de mis productos ──────────────────────
    my_product_ids = [p.id for p in Product.query.filter_by(vendor_id=me.id).all()]

    total_sold = db.session.query(func.sum(OrderItem.quantity))\
        .filter(OrderItem.product_id.in_(my_product_ids)).scalar() or 0

    total_revenue = db.session.query(
        func.sum(OrderItem.quantity * OrderItem.unit_price)
    ).filter(OrderItem.product_id.in_(my_product_ids)).scalar() or 0

    # ─── Ventas últimos 7 días ────────────────────────
    from datetime import datetime, timedelta, timezone
    today = datetime.now(timezone.utc).date()
    days  = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    sales_by_day = []
    for day in days:
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end   = start + timedelta(days=1)
        total = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price))\
            .join(Order)\
            .filter(
                OrderItem.product_id.in_(my_product_ids),
                Order.created_at >= start,
                Order.created_at < end,
            ).scalar() or 0
        sales_by_day.append(float(total))

    day_labels = [d.strftime('%d/%m') for d in days]

    # ─── Top 5 productos más vendidos ────────────────
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label("total_sold"),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")
    ).join(OrderItem)\
     .filter(Product.vendor_id == me.id)\
     .group_by(Product.id)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(5).all()

    top_names   = [p.name for p in top_products]
    top_sales   = [int(p.total_sold) for p in top_products]
    top_revenue = [float(p.revenue) for p in top_products]

    # ─── Pedidos recientes con mis productos ──────────
    recent_items = db.session.query(OrderItem)\
        .filter(OrderItem.product_id.in_(my_product_ids))\
        .order_by(OrderItem.id.desc()).limit(8).all()

    return render_template("vendor/dashboard.html",
        me=me,
        my_products=my_products,
        total_products=total_products,
        low_stock=low_stock,
        total_sold=total_sold,
        total_revenue=total_revenue,
        day_labels=json.dumps(day_labels),
        sales_by_day=json.dumps(sales_by_day),
        top_names=json.dumps(top_names),
        top_sales=json.dumps(top_sales),
        top_revenue=top_revenue,
        recent_items=recent_items,
        top_products=top_products,
    )


@vendor_bp.route("/products")
def products():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    page     = request.args.get("page", 1, type=int)
    products = Product.query.filter_by(vendor_id=me.id)\
                     .order_by(Product.created_at.desc())\
                     .paginate(page=page, per_page=10)
    return render_template("vendor/products.html", products=products)


@vendor_bp.route("/products/create", methods=["GET", "POST"])
def create_product():
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    cats = Category.query.filter_by(is_active=True).all()

    if request.method == "POST":
        name        = sanitize(request.form.get("name", "").strip())
        description = sanitize_html(request.form.get("description", "").strip())
        price       = request.form.get("price", 0)
        stock       = request.form.get("stock", 0)
        category_id = request.form.get("category_id") or None
        image_url   = request.form.get("image_url", "").strip() or None

        # Archivo subido tiene prioridad sobre URL
        file = request.files.get("image_file")
        if file and file.filename and allowed_file(file.filename):
            filename  = secure_filename(f"{me.id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = f"/static/uploads/products/{filename}"

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash("Precio y stock deben ser numéricos.", "danger")
            return render_template("vendor/product_form.html", categories=cats, product=None)

        min_stock = int(request.form.get("min_stock", 5))
        # en create_product:
        product = Product(
            name=name, description=description, price=price,
            stock=stock, vendor_id=me.id, category_id=category_id,
            image_url=image_url, min_stock=min_stock
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Producto '{name}' creado.", "success")
        return redirect(url_for("vendor.products"))

    return render_template("vendor/product_form.html", categories=cats, product=None)


@vendor_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    product = Product.query.filter_by(id=product_id, vendor_id=me.id).first_or_404()
    cats    = Category.query.filter_by(is_active=True).all()

    if request.method == "POST":
        from app.models.product import PriceHistory
        product.name        = sanitize(request.form.get("name", "").strip())
        product.description = sanitize_html(request.form.get("description", "").strip())
        product.category_id = request.form.get("category_id") or None
        image_url           = request.form.get("image_url", "").strip() or None

        file = request.files.get("image_file")
        if file and file.filename and allowed_file(file.filename):
            filename      = secure_filename(f"{me.id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url     = f"/static/uploads/products/{filename}"

        if image_url:
            product.image_url = image_url

        try:
            new_price = float(request.form.get("price", 0))
            new_stock = int(request.form.get("stock", 0))
            min_stock = int(request.form.get("min_stock", 5))

            # Registrar historial si cambia el precio
            if float(product.price) != new_price:
                history = PriceHistory(
                    product_id=product.id,
                    old_price=product.price,
                    new_price=new_price,
                    changed_by=me.id,
                )
                db.session.add(history)

            product.price     = new_price
            product.stock     = new_stock
            product.min_stock = min_stock

        except ValueError:
            flash("Precio y stock inválidos.", "danger")
            return render_template("vendor/product_form.html", categories=cats, product=product)

        db.session.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("vendor.products"))

    return render_template("vendor/product_form.html", categories=cats, product=product)


@vendor_bp.route("/products/<int:product_id>/delete")
def delete_product(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    product = Product.query.filter_by(id=product_id, vendor_id=me.id).first_or_404()
    product.is_active = False
    db.session.commit()
    flash("Producto desactivado.", "info")
    return redirect(url_for("vendor.products"))

@vendor_bp.route("/products/<int:product_id>/discounts", methods=["GET", "POST"])
def manage_discounts(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    product = Product.query.filter_by(id=product_id, vendor_id=me.id).first_or_404()

    if request.method == "POST":
        from app.models.product import QuantityDiscount
        min_qty  = int(request.form.get("min_qty", 0))
        discount = float(request.form.get("discount", 0))

        if min_qty < 2:
            flash("La cantidad mínima debe ser al menos 2.", "warning")
        elif discount <= 0 or discount >= 100:
            flash("El descuento debe ser entre 1% y 99%.", "warning")
        else:
            qd = QuantityDiscount(product_id=product.id, min_qty=min_qty, discount=discount)
            db.session.add(qd)
            db.session.commit()
            flash(f"Descuento agregado: {min_qty}+ unidades → {discount}% OFF", "success")

        return redirect(url_for("vendor.manage_discounts", product_id=product_id))

    return render_template("vendor/discounts.html", product=product)


@vendor_bp.route("/products/discounts/<int:discount_id>/delete")
def delete_discount(discount_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    from app.models.product import QuantityDiscount
    discount = QuantityDiscount.query.get_or_404(discount_id)
    product  = Product.query.filter_by(id=discount.product_id, vendor_id=me.id).first_or_404()
    db.session.delete(discount)
    db.session.commit()
    flash("Descuento eliminado.", "info")
    return redirect(url_for("vendor.manage_discounts", product_id=product.id))

@vendor_bp.route("/products/<int:product_id>/price-history")
def price_history(product_id):
    me = get_user()
    if not me:
        return redirect(url_for("auth.login"))
    product = Product.query.filter_by(id=product_id, vendor_id=me.id).first_or_404()
    history = PriceHistory.query.filter_by(product_id=product_id)\
                .order_by(PriceHistory.changed_at.desc()).all()
    return render_template("vendor/price_history.html", product=product, history=history)