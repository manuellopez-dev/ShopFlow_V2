// ─── Sistema de Toast Notifications ──────────────────

function showToast(message, type = "success", duration = 3500) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const colors = {
    success: { bg: "var(--success-bg)", border: "#a7f3d0", color: "var(--success)", icon: "check-circle" },
    danger:  { bg: "var(--danger-bg)",  border: "#fecaca", color: "var(--danger)",  icon: "x-circle" },
    warning: { bg: "var(--warning-bg)", border: "#fde68a", color: "var(--warning)", icon: "alert-triangle" },
    info:    { bg: "var(--info-bg)",    border: "#bae6fd", color: "var(--info)",    icon: "info" },
  };

  const c = colors[type] || colors.info;

  const toast = document.createElement("div");
  toast.style.cssText = `
    background: ${c.bg};
    border: 1px solid ${c.border};
    color: ${c.color};
    padding: 0.85rem 1.25rem;
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    pointer-events: all;
    cursor: pointer;
    max-width: 320px;
    animation: toastIn 0.3s cubic-bezier(0.34,1.56,0.64,1) both;
    backdrop-filter: blur(10px);
  `;

  toast.innerHTML = `
    <i data-lucide="${c.icon}" style="width:16px;height:16px;flex-shrink:0;"></i>
    <span>${message}</span>
  `;

  toast.addEventListener("click", () => removeToast(toast));
  container.appendChild(toast);
  lucide.createIcons();

  const timer = setTimeout(() => removeToast(toast), duration);
  toast._timer = timer;

  return toast;
}

function removeToast(toast) {
  clearTimeout(toast._timer);
  toast.style.animation = "toastOut 0.25s ease both";
  setTimeout(() => toast.remove(), 250);
}

// ─── Actualizar contador del carrito ─────────────────
function updateCartBadge(count) {
  const badge = document.getElementById("cart-badge");
  if (!badge) return;
  if (count > 0) {
    badge.textContent = count;
    badge.style.display = "flex";
  } else {
    badge.style.display = "none";
  }
}