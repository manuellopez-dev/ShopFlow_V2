// ─── Selector de cantidad ─────────────────────────
function changeQty(delta) {
  const input = document.getElementById("qty-input");
  if (!input) return;
  const max = parseInt(input.max) || 99;
  const min = parseInt(input.min) || 1;
  let val = parseInt(input.value) + delta;
  input.value = Math.min(Math.max(val, min), max);
}

// ─── Star rating interactivo ──────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const labels = document.querySelectorAll(".star-label");
  const inputs = document.querySelectorAll("input[name='rating']");

  function updateStars(rating) {
    labels.forEach((label, i) => {
      const icon = label.querySelector("i");
      if (i < rating) {
        icon.style.stroke = "#f59e0b";
        icon.style.fill   = "#f59e0b";
      } else {
        icon.style.stroke = "#e2e8f0";
        icon.style.fill   = "none";
      }
    });
  }

  // Estado inicial
  const checked = document.querySelector("input[name='rating']:checked");
  if (checked) updateStars(parseInt(checked.value));

  labels.forEach((label, i) => {
    label.style.cursor = "pointer";

    label.addEventListener("mouseenter", () => updateStars(i + 1));

    label.addEventListener("mouseleave", () => {
      const checked = document.querySelector("input[name='rating']:checked");
      updateStars(checked ? parseInt(checked.value) : 0);
    });

    label.addEventListener("click", () => {
      inputs[i].checked = true;
      updateStars(i + 1);
    });
  });
});