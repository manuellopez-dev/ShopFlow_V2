from flask import render_template_string
from flask_mail import Message
from app.extensions import mail

STATUS_LABELS = {
    "pending":   ("⏳", "Pendiente",  "pending"),
    "confirmed": ("✅", "Confirmado", "confirmed"),
    "shipped":   ("🚚", "En camino",  "shipped"),
    "delivered": ("📦", "Entregado",  "delivered"),
    "cancelled": ("❌", "Cancelado",  "cancelled"),
}

STATUS_MESSAGES = {
    "pending":   "Tu pedido ha sido recibido y está en espera de confirmación.",
    "confirmed": "¡Tu pedido ha sido confirmado y está siendo preparado!",
    "shipped":   "¡Tu pedido está en camino! Pronto llegará a tu puerta.",
    "delivered": "¡Tu pedido ha sido entregado! Esperamos que disfrutes tu compra.",
    "cancelled": "Tu pedido ha sido cancelado. Si tienes dudas, contáctanos.",
}

RESET_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body { margin:0; padding:0; background:#f0f4ff; font-family:Arial,sans-serif; }
  .wrapper { max-width:580px; margin:0 auto; padding:2rem 1rem; }
  .card { background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(15,23,42,0.08); }
  .header { background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#1d4ed8 100%); padding:2rem; text-align:center; }
  .header h1 { color:white; margin:0; font-size:1.4rem; font-weight:800; }
  .header p  { color:#93c5fd; margin:0.5rem 0 0; font-size:0.875rem; }
  .body { padding:2rem; }
  .body p { color:#475569; font-size:0.9rem; line-height:1.7; margin:0 0 1rem; }
  .btn { display:inline-block; background:#2563eb; color:white; padding:0.75rem 2rem; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.9rem; }
  .footer { text-align:center; padding:1.5rem; color:#94a3b8; font-size:0.78rem; }
</style>
</head><body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <p style="color:white;font-size:1.2rem;font-weight:800;margin:0 0 0.5rem;">🛍️ ShopFlow</p>
      <h1>Restablecer contraseña</h1>
      <p>Recibimos una solicitud de cambio</p>
    </div>
    <div class="body">
      <p>Hola <strong>{{ name }}</strong>,</p>
      <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en ShopFlow.</p>
      <div style="text-align:center; margin:1.5rem 0;">
        <a href="{{ reset_url }}" class="btn">Restablecer contraseña</a>
      </div>
      <p style="font-size:0.8rem; color:#94a3b8;">
        Este enlace expira en <strong>15 minutos</strong>.<br>
        Si no solicitaste esto, ignora este correo.
      </p>
    </div>
  </div>
  <div class="footer">ShopFlow &copy; 2026 — Sistema de Comercio Electrónico</div>
</div>
</body></html>
"""

ORDER_STATUS_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body { margin:0; padding:0; background:#f0f4ff; font-family:Arial,sans-serif; }
  .wrapper { max-width:580px; margin:0 auto; padding:2rem 1rem; }
  .card { background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(15,23,42,0.08); }
  .header { background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#1d4ed8 100%); padding:2rem; text-align:center; }
  .header h1 { color:white; margin:0; font-size:1.4rem; font-weight:800; }
  .header p  { color:#93c5fd; margin:0.5rem 0 0; font-size:0.875rem; }
  .body { padding:2rem; }
  .body p { color:#475569; font-size:0.9rem; line-height:1.7; margin:0 0 1rem; }
  .btn { display:inline-block; background:#2563eb; color:white; padding:0.75rem 2rem; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.9rem; }
  .status-box { border-radius:10px; padding:1.25rem; margin:1.25rem 0; text-align:center; }
  .status-pending   { background:#fffbeb; border:1px solid #fde68a; color:#d97706; }
  .status-confirmed { background:#f0f9ff; border:1px solid #bae6fd; color:#0284c7; }
  .status-shipped   { background:#fdf4ff; border:1px solid #e9d5ff; color:#7c3aed; }
  .status-delivered { background:#ecfdf5; border:1px solid #a7f3d0; color:#059669; }
  .status-cancelled { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; }
  .status-label { font-size:1.1rem; font-weight:800; margin:0; }
  .details { background:#f8fafc; border-radius:10px; padding:1.25rem; margin:1rem 0; }
  .detail-row { display:flex; justify-content:space-between; padding:0.5rem 0; border-bottom:1px solid #e2e8f0; font-size:0.875rem; }
  .detail-row:last-child { border-bottom:none; }
  .detail-label { color:#64748b; }
  .detail-value { color:#0f172a; font-weight:600; }
  .footer { text-align:center; padding:1.5rem; color:#94a3b8; font-size:0.78rem; }
</style>
</head><body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <p style="color:white;font-size:1.2rem;font-weight:800;margin:0 0 0.5rem;">🛍️ ShopFlow</p>
      <h1>Actualización de pedido</h1>
      <p>Pedido #{{ order_id }}</p>
    </div>
    <div class="body">
      <p>Hola <strong>{{ name }}</strong>,</p>
      <p>{{ status_message }}</p>
      <div class="status-box status-{{ status_key }}">
        <p class="status-label">{{ status_icon }} {{ status_label }}</p>
      </div>
      <div class="details">
        <div class="detail-row">
          <span class="detail-label">Número de pedido</span>
          <span class="detail-value">#{{ order_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Total</span>
          <span class="detail-value">${{ total }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Estado</span>
          <span class="detail-value">{{ status_label }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Fecha</span>
          <span class="detail-value">{{ date }}</span>
        </div>
      </div>
      <div style="text-align:center; margin-top:1.5rem;">
        <a href="{{ orders_url }}" class="btn">Ver mis pedidos</a>
      </div>
    </div>
  </div>
  <div class="footer">ShopFlow &copy; 2026 — Si tienes dudas, contáctanos.</div>
</div>
</body></html>
"""

LOW_STOCK_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body { margin:0; padding:0; background:#f0f4ff; font-family:Arial,sans-serif; }
  .wrapper { max-width:580px; margin:0 auto; padding:2rem 1rem; }
  .card { background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(15,23,42,0.08); }
  .header { background:linear-gradient(135deg,#92400e 0%,#d97706 100%); padding:2rem; text-align:center; }
  .header h1 { color:white; margin:0; font-size:1.4rem; font-weight:800; }
  .header p  { color:#fde68a; margin:0.5rem 0 0; font-size:0.875rem; }
  .body { padding:2rem; }
  .body p { color:#475569; font-size:0.9rem; line-height:1.7; margin:0 0 1rem; }
  .btn { display:inline-block; background:#2563eb; color:white; padding:0.75rem 2rem;
         border-radius:8px; text-decoration:none; font-weight:700; font-size:0.9rem; }
  .alert-box { background:#fffbeb; border:1px solid #fde68a; border-radius:10px;
               padding:1.25rem; margin:1.25rem 0; text-align:center; }
  .alert-label { font-size:1.1rem; font-weight:800; color:#d97706; margin:0; }
  .details { background:#f8fafc; border-radius:10px; padding:1.25rem; margin:1rem 0; }
  .detail-row { display:flex; justify-content:space-between; padding:0.5rem 0;
                border-bottom:1px solid #e2e8f0; font-size:0.875rem; }
  .detail-row:last-child { border-bottom:none; }
  .detail-label { color:#64748b; }
  .detail-value { color:#0f172a; font-weight:600; }
  .footer { text-align:center; padding:1.5rem; color:#94a3b8; font-size:0.78rem; }
</style>
</head><body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <p style="color:white;font-size:1.2rem;font-weight:800;margin:0 0 0.5rem;">🛍️ ShopFlow</p>
      <h1>⚠️ Stock bajo</h1>
      <p>Alerta de inventario</p>
    </div>
    <div class="body">
      <p>Hola <strong>{{ name }}</strong>,</p>
      <p>Uno de tus productos tiene stock bajo y puede agotarse pronto.</p>
      <div class="alert-box">
        <p class="alert-label">⚠️ Stock bajo detectado</p>
      </div>
      <div class="details">
        <div class="detail-row">
          <span class="detail-label">Producto</span>
          <span class="detail-value">{{ product_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Stock actual</span>
          <span class="detail-value" style="color:#dc2626;">{{ current_stock }} unidades</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Stock mínimo</span>
          <span class="detail-value">{{ min_stock }} unidades</span>
        </div>
      </div>
      <p>Te recomendamos reabastecer este producto a la brevedad.</p>
      <div style="text-align:center; margin-top:1.5rem;">
        <a href="{{ products_url }}" class="btn">Ver mis productos</a>
      </div>
    </div>
  </div>
  <div class="footer">ShopFlow &copy; 2026 — Sistema de Comercio Electrónico</div>
</div>
</body></html>
"""

VENDOR_SALE_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body { margin:0; padding:0; background:#f0f4ff; font-family:Arial,sans-serif; }
  .wrapper { max-width:580px; margin:0 auto; padding:2rem 1rem; }
  .card { background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(15,23,42,0.08); }
  .header { background:linear-gradient(135deg,#059669 0%,#047857 100%); padding:2rem; text-align:center; }
  .header h1 { color:white; margin:0; font-size:1.4rem; font-weight:800; }
  .header p  { color:#a7f3d0; margin:0.5rem 0 0; font-size:0.875rem; }
  .body { padding:2rem; }
  .body p { color:#475569; font-size:0.9rem; line-height:1.7; margin:0 0 1rem; }
  .btn { display:inline-block; background:#059669; color:white; padding:0.75rem 2rem;
         border-radius:8px; text-decoration:none; font-weight:700; font-size:0.9rem; }
  .details { background:#f8fafc; border-radius:10px; padding:1.25rem; margin:1rem 0; }
  .detail-row { display:flex; justify-content:space-between; padding:0.5rem 0;
                border-bottom:1px solid #e2e8f0; font-size:0.875rem; }
  .detail-row:last-child { border-bottom:none; }
  .detail-label { color:#64748b; }
  .detail-value { color:#0f172a; font-weight:600; }
  .footer { text-align:center; padding:1.5rem; color:#94a3b8; font-size:0.78rem; }
  .items-table { width:100%; border-collapse:collapse; font-size:0.8rem; margin:1rem 0; }
  .items-table th { background:#f1f5f9; padding:8px 12px; text-align:left; color:#64748b; }
  .items-table td { padding:8px 12px; border-bottom:1px solid #e2e8f0; }
</style>
</head><body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <p style="color:white;font-size:1.2rem;font-weight:800;margin:0 0 0.5rem;">🛍️ ShopFlow</p>
      <h1>¡Nueva venta!</h1>
      <p>Pedido #{{ order_id }}</p>
    </div>
    <div class="body">
      <p>Hola <strong>{{ vendor_name }}</strong>,</p>
      <p>¡Tienes una nueva venta! Un cliente ha comprado tus productos.</p>
      <table class="items-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {{ items_rows }}
        </tbody>
      </table>
      <div class="details">
        <div class="detail-row">
          <span class="detail-label">Pedido</span>
          <span class="detail-value">#{{ order_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Fecha</span>
          <span class="detail-value">{{ date }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Total del pedido</span>
          <span class="detail-value">${{ total }}</span>
        </div>
      </div>
      <div style="text-align:center; margin-top:1.5rem;">
        <a href="{{ dashboard_url }}" class="btn">Ver mi dashboard</a>
      </div>
    </div>
  </div>
  <div class="footer">ShopFlow &copy; 2026</div>
</div>
</body></html>
"""

def send_vendor_sale_email(vendor, order):
    from flask import request as flask_request

    # Solo items del vendor
    vendor_items = [item for item in order.items if item.product.vendor_id == vendor.id]
    if not vendor_items:
        return

    items_rows = ""
    for item in vendor_items:
        items_rows += f"""
        <tr>
          <td>{item.product.name}</td>
          <td>{item.quantity}</td>
          <td>${float(item.unit_price * item.quantity):,.2f}</td>
        </tr>
        """

    try:
        base_url = flask_request.host_url.rstrip("/")
        dashboard_url = f"{base_url}/vendor/dashboard"
    except Exception:
        dashboard_url = "http://localhost:5000/vendor/dashboard"

    body = render_template_string(
        VENDOR_SALE_TEMPLATE,
        vendor_name=vendor.name,
        order_id=order.id,
        items_rows=items_rows,
        total=f"{float(order.total):,.2f}",
        date=order.created_at.strftime("%d/%m/%Y %H:%M"),
        dashboard_url=dashboard_url,
    )
    msg = Message(
        subject=f"🎉 Nueva venta — Pedido #{order.id} | ShopFlow",
        recipients=[vendor.email],
        html=body,
    )
    mail.send(msg)


def send_low_stock_email(vendor, product):
    from flask import request as flask_request
    try:
        base_url     = flask_request.host_url.rstrip("/")
        products_url = f"{base_url}/vendor/products"
    except Exception:
        products_url = "http://localhost:5000/vendor/products"

    body = render_template_string(
        LOW_STOCK_TEMPLATE,
        name=vendor.name,
        product_name=product.name,
        current_stock=product.stock,
        min_stock=product.min_stock,
        products_url=products_url,
    )
    msg = Message(
        subject=f"⚠️ Stock bajo: {product.name} | ShopFlow",
        recipients=[vendor.email],
        html=body,
    )
    mail.send(msg)


def send_password_reset_email(user, reset_url: str):
    body = render_template_string(
        RESET_TEMPLATE,
        name=user.name,
        reset_url=reset_url,
    )
    msg = Message(
        subject="Restablecer contraseña — ShopFlow",
        recipients=[user.email],
        html=body,
    )
    mail.send(msg)


def send_order_status_email(user, order):
    from flask import request as flask_request

    status_key = str(order.status).replace("OrderStatus.", "").lower()

    result = STATUS_LABELS.get(status_key)
    if result:
        icon, label, key = result
    else:
        icon, label, key = "📋", status_key.title(), status_key

    message = STATUS_MESSAGES.get(status_key, "El estado de tu pedido ha sido actualizado.")

    try:
        base_url   = flask_request.host_url.rstrip("/")
        orders_url = f"{base_url}/shop/orders"
    except Exception:
        orders_url = "http://localhost:5000/shop/orders"

    body = render_template_string(
        ORDER_STATUS_TEMPLATE,
        name=user.name,
        order_id=order.id,
        status_key=key,
        status_icon=icon,
        status_label=label,
        status_message=message,
        total=f"{float(order.total):,.2f}",
        date=order.created_at.strftime("%d/%m/%Y %H:%M"),
        orders_url=orders_url,
    )
    msg = Message(
        subject=f"{icon} Tu pedido #{order.id} — {label} | ShopFlow",
        recipients=[user.email],
        html=body,
    )
    mail.send(msg)