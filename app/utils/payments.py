import stripe
import paypalrestsdk
import os

# ─── Stripe ──────────────────────────────────────────
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_payment_intent(amount: float, currency: str = "mxn"):
    """Crea un PaymentIntent de Stripe. amount en pesos."""
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # Stripe usa centavos
        currency=currency,
        payment_method_types=["card"],
    )
    return intent


# ─── PayPal ───────────────────────────────────────────
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET"),
})


def create_paypal_payment(amount: float, return_url: str, cancel_url: str):
    """Crea un pago de PayPal y retorna la URL de aprobación."""
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url,
        },
        "transactions": [{
            "amount": {
                "total": f"{amount:.2f}",
                "currency": "MXN",
            },
            "description": "Compra en ShopFlow",
        }]
    })
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return payment.id, link.href
    return None, None


def execute_paypal_payment(payment_id: str, payer_id: str):
    """Ejecuta el pago después de que el usuario aprueba en PayPal."""
    payment = paypalrestsdk.Payment.find(payment_id)
    return payment.execute({"payer_id": payer_id})