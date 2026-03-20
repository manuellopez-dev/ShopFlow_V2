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

# ─── Base CSS compartido ───────────────────────────────
BASE_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #f0f4ff; font-family: 'Segoe UI', Arial, sans-serif; }
  .wrapper { max-width: 600px; margin: 0 auto; padding: 2rem 1rem; }
  .card { background: #ffffff; border-radius: 20px; overflow: hidden;
          box-shadow: 0 8px 40px rgba(15,23,42,0.10); }
  .header { padding: 2.5rem 2rem; text-align: center; position: relative; }
  .header-logo { font-size: 1rem; font-weight: 800; color: rgba(255,255,255,0.9);
                 margin-bottom: 1rem; letter-spacing: 0.5px; }
  .header h1 { color: white; margin: 0; font-size: 1.6rem; font-weight: 800;
               letter-spacing: -0.5px; line-height: 1.2; }
  .header p { margin: 0.5rem 0 0; font-size: 0.875rem; opacity: 0.8; }
  .header-icon { width: 64px; height: 64px; background: rgba(255,255,255,0.15);
                 border-radius: 50%; display: flex; align-items: center;
                 justify-content: center; margin: 0 auto 1rem; font-size: 1.75rem; }
  .body { padding: 2rem; }
  .body p { color: #475569; font-size: 0.9rem; line-height: 1.75; margin: 0 0 1rem; }
  .greeting { font-size: 1rem; color: #1e293b; font-weight: 600; }
  .btn { display: inline-block; padding: 0.85rem 2.5rem; border-radius: 10px;
         text-decoration: none; font-weight: 700; font-size: 0.9rem;
         letter-spacing: 0.2px; }
  .btn-center { text-align: center; margin: 1.75rem 0; }
  .details { background: #f8fafc; border-radius: 12px; padding: 0;
             margin: 1.25rem 0; overflow: hidden; border: 1px solid #e2e8f0; }
  .detail-row { display: flex; justify-content: space-between; align-items: center;
                padding: 0.75rem 1.25rem; border-bottom: 1px solid #e2e8f0;
                font-size: 0.875rem; }
  .detail-row:last-child { border-bottom: none; }
  .detail-label { color: #64748b; }
  .detail-value { color: #0f172a; font-weight: 700; }
  .status-box { border-radius: 12px; padding: 1.25rem; margin: 1.25rem 0;
                text-align: center; }
  .status-label { font-size: 1.2rem; font-weight: 800; margin: 0; }
  .status-pending   { background: #fffbeb; border: 2px solid #fde68a; color: #d97706; }
  .status-confirmed { background: #f0f9ff; border: 2px solid #bae6fd; color: #0284c7; }
  .status-shipped   { background: #fdf4ff; border: 2px solid #e9d5ff; color: #7c3aed; }
  .status-delivered { background: #ecfdf5; border: 2px solid #a7f3d0; color: #059669; }
  .status-cancelled { background: #fef2f2; border: 2px solid #fecaca; color: #dc2626; }
  .divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
  .footer { text-align: center; padding: 1.5rem; }
  .footer p { color: #94a3b8; font-size: 0.75rem; line-height: 1.6; margin: 0; }
  .footer-logo { font-weight: 800; color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem; }
  .items-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  .items-table th { background: #f1f5f9; padding: 10px 14px; text-align: left;
                    color: #64748b; font-weight: 600; font-size: 0.75rem;
                    text-transform: uppercase; letter-spacing: 0.5px; }
  .items-table td { padding: 10px 14px; border-bottom: 1px solid #e2e8f0; color: #1e293b; }
  .items-table tr:last-child td { border-bottom: none; }
  .alert-box { background: #fffbeb; border: 2px solid #fde68a; border-radius: 12px;
               padding: 1.25rem; margin: 1.25rem 0; text-align: center; }
  .note { background: #f8fafc; border-left: 4px solid #2563eb; border-radius: 0 8px 8px 0;
          padding: 0.85rem 1.25rem; font-size: 0.8rem; color: #64748b; margin: 1rem 0; }
"""

# ─── Template: Reset de contraseña ────────────────────
RESET_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>""" + BASE_CSS + """</style></head><body>
<div class="wrapper">
  <div class="card">
    <div class="header" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#2563eb 100%);">
      <div class="header-logo">🛍️ ShopFlow</div>
      <div class="header-icon">🔐</div>
      <h1>Restablecer contraseña</h1>
      <p style="color:#93c5fd;">Recibimos una solicitud de cambio</p>
    </div>
    <div class="body">
      <p class="greeting">Hola, {{ name }} 👋</p>
      <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en ShopFlow. Si fuiste tú, haz clic en el botón de abajo para continuar.</p>
      <div class="btn-center">
        <a href="{{ reset_url }}" class="btn"
           style="background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white;">
          🔑 Restablecer contraseña
        </a>
      </div>
      <div class="note">
        ⏱️ Este enlace expira en <strong>15 minutos</strong>.<br>
        Si no solicitaste esto, puedes ignorar este correo con seguridad.
      </div>
    </div>
  </div>
  <div class="footer">
    <p class="footer-logo">ShopFlow</p>
    <p>© 2026 ShopFlow — Sistema de Comercio Electrónico<br>
    Este es un correo automático, por favor no respondas.</p>
  </div>
</div>
</body></html>
"""

# ─── Template: Estado de pedido ───────────────────────
ORDER_STATUS_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>""" + BASE_CSS + """</style></head><body>
<div class="wrapper">
  <div class="card">
    <div class="header" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#2563eb 100%);">
      <div class="header-logo">🛍️ ShopFlow</div>
      <div class="header-icon">{{ status_icon }}</div>
      <h1>Actualización de pedido</h1>
      <p style="color:#93c5fd;">Pedido #{{ order_id }}</p>
    </div>
    <div class="body">
      <p class="greeting">Hola, {{ name }} 👋</p>
      <p>{{ status_message }}</p>
      <div class="status-box status-{{ status_key }}">
        <p class="status-label">{{ status_icon }} {{ status_label }}</p>
      </div>
      <div class="details">
        <div class="detail-row">
          <span class="detail-label">📦 Número de pedido</span>
          <span class="detail-value">#{{ order_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">💰 Total</span>
          <span class="detail-value">${{ total }} MXN</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">🏷️ Estado</span>
          <span class="detail-value">{{ status_label }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">📅 Fecha</span>
          <span class="detail-value">{{ date }}</span>
        </div>
      </div>
      <div class="btn-center">
        <a href="{{ orders_url }}" class="btn"
           style="background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white;">
          Ver mis pedidos →
        </a>
      </div>
    </div>
  </div>
  <div class="footer">
    <p class="footer-logo">ShopFlow</p>
    <p>© 2026 ShopFlow — Si tienes dudas, contáctanos.<br>
    Este es un correo automático, por favor no respondas.</p>
  </div>
</div>
</body></html>
"""

# ─── Template: Stock bajo ──────────────────────────────
LOW_STOCK_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>""" + BASE_CSS + """</style></head><body>
<div class="wrapper">
  <div class="card">
    <div class="header" style="background:linear-gradient(135deg,#92400e 0%,#d97706 100%);">
      <div class="header-logo">🛍️ ShopFlow</div>
      <div class="header-icon">⚠️</div>
      <h1>Alerta de stock bajo</h1>
      <p style="color:#fde68a;">Inventario por agotarse</p>
    </div>
    <div class="body">
      <p class="greeting">Hola, {{ name }} 👋</p>
      <p>Uno de tus productos tiene stock bajo y puede agotarse pronto. Te recomendamos reabastecer a la brevedad.</p>
      <div class="alert-box">
        <p style="font-size:1.2rem; font-weight:800; color:#d97706; margin:0;">
          ⚠️ Stock bajo detectado
        </p>
      </div>
      <div class="details">
        <div class="detail-row">
          <span class="detail-label">📦 Producto</span>
          <span class="detail-value">{{ product_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">🔢 Stock actual</span>
          <span class="detail-value" style="color:#dc2626;">{{ current_stock }} unidades</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">📉 Stock mínimo</span>
          <span class="detail-value">{{ min_stock }} unidades</span>
        </div>
      </div>
      <div class="btn-center">
        <a href="{{ products_url }}" class="btn"
           style="background:linear-gradient(135deg,#d97706,#b45309); color:white;">
          Gestionar productos →
        </a>
      </div>
    </div>
  </div>
  <div class="footer">
    <p class="footer-logo">ShopFlow</p>
    <p>© 2026 ShopFlow — Sistema de Comercio Electrónico</p>
  </div>
</div>
</body></html>
"""

# ─── Template: Nueva venta al vendor ──────────────────
VENDOR_SALE_TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>""" + BASE_CSS + """</style></head><body>
<div class="wrapper">
  <div class="card">
    <div class="header" style="background:linear-gradient(135deg,#064e3b 0%,#059669 100%);">
      <div class="header-logo">🛍️ ShopFlow</div>
      <div class="header-icon">🎉</div>
      <h1>¡Nueva venta!</h1>
      <p style="color:#a7f3d0;">Pedido #{{ order_id }}</p>
    </div>
    <div class="body">
      <p class="greeting">Hola, {{ vendor_name }} 👋</p>
      <p>¡Excelentes noticias! Un cliente acaba de comprar tus productos. Aquí tienes el resumen:</p>
      <div class="details" style="margin-bottom:0;">
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
      </div>
      <div class="details" style="margin-top:1rem;">
        <div class="detail-row">
          <span class="detail-label">🧾 Pedido</span>
          <span class="detail-value">#{{ order_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">📅 Fecha</span>
          <span class="detail-value">{{ date }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">💰 Total del pedido</span>
          <span class="detail-value" style="color:#059669;">${{ total }} MXN</span>
        </div>
      </div>
      <div class="btn-center">
        <a href="{{ dashboard_url }}" class="btn"
           style="background:linear-gradient(135deg,#059669,#047857); color:white;">
          Ver mi dashboard →
        </a>
      </div>
    </div>
  </div>
  <div class="footer">
    <p class="footer-logo">ShopFlow</p>
    <p>© 2026 ShopFlow — ¡Sigue vendiendo! 🚀</p>
  </div>
</div>
</body></html>
"""


# ─── Funciones ─────────────────────────────────────────
def send_password_reset_email(user, reset_url: str):
    body = render_template_string(RESET_TEMPLATE, name=user.name, reset_url=reset_url)
    msg  = Message(
        subject="🔐 Restablecer contraseña — ShopFlow",
        recipients=[user.email],
        html=body,
    )
    mail.send(msg)


def send_order_status_email(user, order):
    from flask import request as flask_request
    status_key = str(order.status).replace("OrderStatus.", "").lower()
    result     = STATUS_LABELS.get(status_key)
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


def send_vendor_sale_email(vendor, order):
    from flask import request as flask_request
    vendor_items = [item for item in order.items if item.product.vendor_id == vendor.id]
    if not vendor_items:
        return
    items_rows = ""
    for item in vendor_items:
        items_rows += f"""
        <tr>
          <td>{item.product.name}</td>
          <td style="text-align:center;">{item.quantity}</td>
          <td style="font-weight:700;">${float(item.unit_price * item.quantity):,.2f}</td>
        </tr>
        """
    try:
        base_url      = flask_request.host_url.rstrip("/")
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