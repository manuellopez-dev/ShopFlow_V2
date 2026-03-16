document.addEventListener("DOMContentLoaded", () => {
  const { orderId, stripePubKey } = window.PAYMENT;

  const stripe   = Stripe(stripePubKey);
  const elements = stripe.elements();

  const style = {
    base: {
      fontFamily:  "Inter, sans-serif",
      fontSize:    "15px",
      color:       "#0f172a",
      "::placeholder": { color: "#94a3b8" }
    }
  };

  // Montar campos separados
  const cardNumber  = elements.create("cardNumber",  { style, showIcon: true });
  const cardExpiry  = elements.create("cardExpiry",  { style });
  const cardCvc     = elements.create("cardCvc",     { style });

  cardNumber.mount("#card-number");
  cardExpiry.mount("#card-expiry");
  cardCvc.mount("#card-cvc");

  // Errores
  [cardNumber, cardExpiry, cardCvc].forEach(el => {
    el.on("change", e => {
      document.getElementById("card-errors").textContent = e.error ? e.error.message : "";
    });
  });

  document.getElementById("stripe-btn").addEventListener("click", async () => {
    const btn = document.getElementById("stripe-btn");
    btn.disabled    = true;
    btn.innerHTML   = '<span class="spinner"></span> Procesando...';

    const res  = await fetch("/payments/stripe/create/" + orderId, { method: "POST" });
    const data = await res.json();

    const result = await stripe.confirmCardPayment(data.client_secret, {
      payment_method: { card: cardNumber }
    });

    if (result.error) {
      document.getElementById("card-errors").textContent = result.error.message;
      btn.disabled  = false;
      btn.innerHTML = '<i data-lucide="lock" style="width:15px;height:15px;"></i> Reintentar pago';
      lucide.createIcons();
      return;
    }

    const confirm = await fetch("/payments/stripe/confirm/" + orderId, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ status: result.paymentIntent.status }),
    });
    const confirmData = await confirm.json();

    if (confirmData.success) {
      window.location.href = confirmData.redirect;
    } else {
      document.getElementById("card-errors").textContent = "Error al confirmar el pago.";
      btn.disabled  = false;
      btn.innerHTML = "Reintentar pago";
    }
  });
});