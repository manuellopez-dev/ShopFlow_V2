def check_low_stock(product, vendor):
    """Verifica si el stock está bajo y envía email al vendor."""
    if product.stock <= product.min_stock and product.stock >= 0:
        try:
            from app.utils.email import send_low_stock_email
            send_low_stock_email(vendor, product)
            print(f"[STOCK] Alerta enviada a {vendor.email} para '{product.name}' (stock: {product.stock})")
        except Exception as e:
            print(f"[STOCK ERROR] {e}")