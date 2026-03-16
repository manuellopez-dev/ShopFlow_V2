async function applyCoupon() {
  const code = document.getElementById("coupon-input").value.trim();
  if (!code) return;

  const formData = new FormData();
  formData.append("coupon_code", code);

  const res  = await fetch("/coupons/apply", { method: "POST", body: formData });
  const data = await res.json();
  const msg  = document.getElementById("coupon-msg");

  if (data.success) {
    msg.style.color = "var(--success)";
    msg.textContent = data.message;
    document.getElementById("discount-row").style.display = "flex";
    document.getElementById("discount-val").textContent   = "-$" + data.discount.toFixed(2);
    document.getElementById("total-val").textContent      = "$" + data.new_total.toFixed(2);
    document.getElementById("coupon-hidden").value        = code;
  } else {
    msg.style.color = "var(--danger)";
    msg.textContent = data.error;
  }
}