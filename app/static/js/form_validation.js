// ─── Validación en tiempo real ────────────────────────

console.log("[FormValidation] Script cargado");

const rules = {
  email: {
    test: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
    msg:  "Ingresa un correo válido."
  },
  password: {
    test: v => v.length >= 8,
    msg:  "Mínimo 8 caracteres."
  },
  name: {
    test: v => v.trim().length >= 2,
    msg:  "Mínimo 2 caracteres."
  },
  price: {
    test: v => !isNaN(v) && parseFloat(v) > 0,
    msg:  "Debe ser un número mayor a 0."
  },
  stock: {
    test: v => !isNaN(v) && parseInt(v) >= 0,
    msg:  "Debe ser un número mayor o igual a 0."
  },
}

function getRule(input) {
  if (input.type === "email")    return rules.email;
  if (input.type === "password") return rules.password;
  if (input.name === "name")     return rules.name;
  if (input.name === "price")    return rules.price;
  if (input.name === "stock")    return rules.stock;
  return null;
}

function showError(input, msg) {
  input.style.borderColor = "var(--danger)";
  input.style.boxShadow   = "0 0 0 3px rgba(220,38,38,0.1)";
  let err = input.parentElement.querySelector(".field-error");
  if (!err) {
    err = document.createElement("div");
    err.className = "field-error";
    input.parentElement.appendChild(err);
  }
  err.textContent = msg;
}

function showSuccess(input) {
  input.style.borderColor = "var(--success)";
  input.style.boxShadow   = "0 0 0 3px rgba(5,150,105,0.1)";
  const err = input.parentElement.querySelector(".field-error");
  if (err) err.remove();
}

function clearState(input) {
  input.style.borderColor = "";
  input.style.boxShadow   = "";
  const err = input.parentElement.querySelector(".field-error");
  if (err) err.remove();
}

function validateInput(input) {
  if (!input.value) { clearState(input); return true; }
  const rule = getRule(input);
  if (!rule) return true;
  if (rule.test(input.value)) {
    showSuccess(input);
    return true;
  } else {
    showError(input, rule.msg);
    return false;
  }
}

// ─── Validar confirmación de contraseña ───────────────
function validateConfirm() {
  const pass    = document.querySelector("input[name='password'], input[name='new_password']");
  const confirm = document.querySelector("input[name='confirm_password']");
  if (!pass || !confirm || !confirm.value) return true;
  if (pass.value === confirm.value) {
    showSuccess(confirm);
    return true;
  } else {
    showError(confirm, "Las contraseñas no coinciden.");
    return false;
  }
}

// ─── Inicializar en todos los formularios ─────────────
// ─── Agregar CSRF token a todos los formularios ───────
document.addEventListener("DOMContentLoaded", () => {
  const token = document.querySelector('meta[name="csrf-token"]');
  if (token) {
    document.querySelectorAll("form[method='POST'], form[method='post']").forEach(form => {
      if (!form.querySelector('input[name="csrf_token"]')) {
        const input = document.createElement("input");
        input.type  = "hidden";
        input.name  = "csrf_token";
        input.value = token.content;
        form.appendChild(input);
      }
    });
  }
});

  // Validar al submit
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", e => {
      let valid = true;
      form.querySelectorAll("input[required], select[required]").forEach(input => {
        if (!input.value.trim()) {
          showError(input, "Este campo es obligatorio.");
          valid = false;
        } else if (!validateInput(input)) {
          valid = false;
        }
      });
      if (!validateConfirm()) valid = false;
      if (!valid) e.preventDefault();
    });
  });
