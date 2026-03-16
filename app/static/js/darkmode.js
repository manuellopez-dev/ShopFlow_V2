// ─── Modo oscuro ──────────────────────────────────────
const DARK_KEY = "shopflow-theme";
const toggle   = document.getElementById("theme-toggle");
const icon     = document.getElementById("theme-icon");

function applyTheme(dark) {
  document.body.classList.toggle("dark", dark);
  if (icon) {
    icon.setAttribute("data-lucide", dark ? "sun" : "moon");
    lucide.createIcons();
  }
}

// Cargar tema guardado
const saved = localStorage.getItem(DARK_KEY);
applyTheme(saved === "dark");

// Toggle al hacer clic
if (toggle) {
  toggle.addEventListener("click", () => {
    const isDark = document.body.classList.contains("dark");
    localStorage.setItem(DARK_KEY, isDark ? "light" : "dark");
    applyTheme(!isDark);
  });
}