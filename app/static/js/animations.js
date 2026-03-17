// ─── Scroll Reveal ────────────────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add("visible"), i * 80);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll(".reveal").forEach(el => revealObserver.observe(el));

// ─── Contador animado en stats ────────────────────────
function animateCounter(el, target) {
  const duration = 1200;
  const start    = performance.now();

  function update(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);
    const value    = eased * target;
    el.textContent = value.toLocaleString("es-MX", { maximumFractionDigits: 0 });
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

document.querySelectorAll(".stat-value").forEach(el => {
  const raw    = el.textContent.replace(/[$,\s]/g, "");
  const target = parseFloat(raw);
  if (!isNaN(target)) animateCounter(el, target);
});

// ─── Auto-ocultar alerts ──────────────────────────────
document.querySelectorAll(".alert").forEach(alert => {
  setTimeout(() => {
    alert.style.transition = "opacity 0.5s ease";
    alert.style.opacity    = "0";
    setTimeout(() => alert.remove(), 500);
  }, 4000);
});

// ─── Ripple en botones ────────────────────────────────
document.querySelectorAll(".btn").forEach(btn => {
  btn.addEventListener("click", function(e) {
    const ripple = document.createElement("span");
    const rect   = this.getBoundingClientRect();
    ripple.style.cssText = `
      position:absolute;
      border-radius:50%;
      background:rgba(255,255,255,0.3);
      width:100px; height:100px;
      left:${e.clientX - rect.left - 50}px;
      top:${e.clientY - rect.top - 50}px;
      transform:scale(0);
      animation:ripple 0.6s ease;
      pointer-events:none;
    `;
    this.style.position = "relative";
    this.style.overflow = "hidden";
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
});

// ─── Página con fade in ───────────────────────────────
document.body.style.opacity = "0";
window.addEventListener("load", () => {
  document.body.style.transition = "opacity 0.3s ease";
  document.body.style.opacity    = "1";
});

// ─── Scroll spy para docs ─────────────────────────────
const docLinks = document.querySelectorAll(".doc-nav-link");
if (docLinks.length > 0) {
  const sections = [...docLinks].map(l => document.querySelector(l.getAttribute("href")));

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(section => {
      if (section && window.scrollY >= section.offsetTop - 120) {
        current = "#" + section.id;
      }
    });
    docLinks.forEach(link => {
      link.classList.toggle("active", link.getAttribute("href") === current);
    });
  });
}

// ─── Add to cart AJAX ─────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".add-to-cart-form").forEach(form => {
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const productId  = form.dataset.product;
      const qty        = form.querySelector(".qty-input")?.value || 1;
      const btn        = form.querySelector("button[type='submit']");
      const originalHTML = btn.innerHTML;

      btn.disabled  = true;
      btn.innerHTML = '<span class="spinner"></span>';

      const formData = new FormData();
      formData.append("qty", qty);

      const res  = await fetch(`/shop/cart/add/${productId}`, {
        method:  "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body:    formData
      });
      const data = await res.json();

      btn.disabled  = false;
      btn.innerHTML = originalHTML;
      lucide.createIcons();

      if (data.success) {
        showToast(data.message, "success");
        updateCartBadge(data.cart_count);
      } else {
        showToast("Error al agregar al carrito.", "danger");
      }
    });
  });
});

// ─── Navbar hamburguesa ───────────────────────────────
const hamburger  = document.getElementById("nav-hamburger");
const navLinks   = document.querySelector(".nav-links");

if (hamburger && navLinks) {
  hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("open");
    const icon = hamburger.querySelector("i");
    const isOpen = navLinks.classList.contains("open");
    icon.setAttribute("data-lucide", isOpen ? "x" : "menu");
    lucide.createIcons();
  });
}

// ─── Toggle filtros catálogo en móvil ─────────────────
const filterToggle  = document.getElementById("filter-toggle");
const catalogSidebar = document.querySelector(".catalog-sidebar");

if (filterToggle && catalogSidebar) {
  filterToggle.addEventListener("click", () => {
    catalogSidebar.classList.toggle("open");
    const isOpen = catalogSidebar.classList.contains("open");
    filterToggle.innerHTML = isOpen
      ? '<i data-lucide="x" style="width:14px;height:14px;"></i> Ocultar filtros'
      : '<i data-lucide="filter" style="width:14px;height:14px;"></i> Filtros y búsqueda';
    lucide.createIcons();
  });
}