// ─── Toast notifications ──────────────────────────────
const TOAST_ICONS = {
  success: "check-circle",
  danger:  "x-circle",
  warning: "alert-triangle",
  info:    "info",
};

function showToast(message, type = "info", duration = 4000) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i data-lucide="${TOAST_ICONS[type] || 'info'}" class="toast-icon"></i>
    <span class="toast-msg">${message}</span>
    <button class="toast-close" onclick="removeToast(this.parentElement)">
      <i data-lucide="x" style="width:14px;height:14px;"></i>
    </button>
  `;

  container.appendChild(toast);
  lucide.createIcons();

  setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
  if (!toast || toast.classList.contains("hiding")) return;
  toast.classList.add("hiding");
  setTimeout(() => toast.remove(), 300);
}

// ─── Convertir alerts de Flask en toasts ─────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach(alert => {
    const msg  = alert.textContent.trim();
    const type = [...alert.classList].find(c => c.startsWith("alert-"))?.replace("alert-", "") || "info";
    showToast(msg, type === "error" ? "danger" : type);
    alert.remove();
  });
});

// ─── Modal de confirmación ────────────────────────────
function confirmModal({ title, desc, confirmText = "Confirmar", cancelText = "Cancelar",
                        type = "danger", onConfirm }) {
  const iconMap = { danger: "trash-2", warning: "alert-triangle" };
  const colorMap = { danger: "var(--danger)", warning: "var(--warning)" };

  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal-box">
      <div class="modal-icon modal-icon-${type}">
        <i data-lucide="${iconMap[type]}"
           style="width:24px;height:24px;stroke:${colorMap[type]};"></i>
      </div>
      <div class="modal-title">${title}</div>
      <div class="modal-desc">${desc}</div>
      <div class="modal-actions">
        <button class="btn btn-outline btn-full" id="modal-cancel">${cancelText}</button>
        <button class="btn btn-danger btn-full" id="modal-confirm"
                style="background:var(--danger);color:white;">${confirmText}</button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  lucide.createIcons();

  overlay.querySelector("#modal-cancel").addEventListener("click", () => overlay.remove());
  overlay.addEventListener("click", e => { if (e.target === overlay) overlay.remove(); });
  overlay.querySelector("#modal-confirm").addEventListener("click", () => {
    overlay.remove();
    onConfirm();
  });
}

// ─── Confirmación en links de eliminar ────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-confirm]").forEach(el => {
    el.addEventListener("click", e => {
      e.preventDefault();
      const title = el.dataset.confirmTitle || "¿Estás seguro?";
      const desc  = el.dataset.confirm;
      const href  = el.href;

      confirmModal({
        title,
        desc,
        confirmText: el.dataset.confirmBtn || "Eliminar",
        type: "danger",
        onConfirm: () => window.location.href = href,
      });
    });
  });
});