// ─── Confirmaciones antes de acciones destructivas ───

function confirmAction(message, callback) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position:fixed; inset:0; background:rgba(0,0,0,0.5);
    display:flex; align-items:center; justify-content:center;
    z-index:10000; backdrop-filter:blur(4px);
    animation:fadeIn 0.2s ease both;
  `;

  overlay.innerHTML = `
    <div style="
      background:var(--surface); border:1px solid var(--border);
      border-radius:var(--radius-xl); padding:2rem; max-width:400px;
      width:90%; box-shadow:var(--shadow-lg);
      animation:scaleIn 0.25s cubic-bezier(0.34,1.56,0.64,1) both;
    ">
      <div style="
        width:48px; height:48px; background:var(--danger-bg);
        border-radius:50%; display:flex; align-items:center;
        justify-content:center; margin:0 auto 1rem;
      ">
        <i data-lucide="alert-triangle" style="width:24px;height:24px;stroke:var(--danger);"></i>
      </div>
      <h3 style="
        font-family:'Plus Jakarta Sans',sans-serif; font-size:1rem;
        font-weight:700; text-align:center; margin-bottom:0.75rem;
        color:var(--text);
      ">¿Estás seguro?</h3>
      <p style="
        color:var(--text-muted); font-size:0.875rem;
        text-align:center; margin-bottom:1.5rem; line-height:1.6;
      ">${message}</p>
      <div style="display:flex; gap:0.75rem;">
        <button id="confirm-cancel" class="btn btn-outline btn-full">
          Cancelar
        </button>
        <button id="confirm-ok" class="btn btn-danger btn-full" style="
          background:var(--danger); color:white; border:none;
        ">
          Confirmar
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  lucide.createIcons();

  document.getElementById("confirm-cancel").addEventListener("click", () => {
    overlay.style.animation = "fadeOut 0.2s ease both";
    setTimeout(() => overlay.remove(), 200);
  });

  document.getElementById("confirm-ok").addEventListener("click", () => {
    overlay.remove();
    callback();
  });

  overlay.addEventListener("click", e => {
    if (e.target === overlay) {
      overlay.style.animation = "fadeOut 0.2s ease both";
      setTimeout(() => overlay.remove(), 200);
    }
  });
}

// ─── Aplicar a links/botones con data-confirm ─────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-confirm]").forEach(el => {
    el.addEventListener("click", e => {
      e.preventDefault();
      const message = el.dataset.confirm;
      const href    = el.href;
      const form    = el.closest("form");

      confirmAction(message, () => {
        if (href) window.location.href = href;
        else if (form) form.submit();
      });
    });
  });
});