// ─── Colores ──────────────────────────────────────────
const accent  = "#1a1a2e";
const gold    = "#c9a96e";
const success = "#2d6a4f";
const danger  = "#c0392b";
const info    = "#1a6eb5";
const purple  = "#5b21b6";

// ─── Ingresos 7 días ──────────────────────────────────
if (document.getElementById("revenueChart")) {
  const revenueCtx = document.getElementById("revenueChart").getContext("2d");
  new Chart(revenueCtx, {
    type: "line",
    data: {
      labels:   window.DASHBOARD.dayLabels,
      datasets: [{
        label:                "Ingresos ($)",
        data:                 window.DASHBOARD.revenueByDay,
        borderColor:          gold,
        backgroundColor:      "rgba(201,169,110,0.12)",
        borderWidth:          2.5,
        pointBackgroundColor: gold,
        pointRadius:          5,
        fill:                 true,
        tension:              0.4,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.05)" } },
        x: { grid: { display: false } }
      }
    }
  });
}

// ─── Pedidos por estado ───────────────────────────────
if (document.getElementById("statusChart")) {
  const statusCtx = document.getElementById("statusChart").getContext("2d");
  new Chart(statusCtx, {
    type: "doughnut",
    data: {
      labels:   Object.keys(window.DASHBOARD.statusData),
      datasets: [{
        data:            Object.values(window.DASHBOARD.statusData),
        backgroundColor: [gold, info, purple, success, danger],
        borderWidth:     2,
        borderColor:     "#fff",
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "right", labels: { font: { family: "Inter" } } }
      },
      cutout: "65%",
    }
  });
}

// ─── Productos más vendidos ───────────────────────────
if (document.getElementById("topChart")) {
  const topCtx = document.getElementById("topChart").getContext("2d");
  new Chart(topCtx, {
    type: "bar",
    data: {
      labels:   window.DASHBOARD.topNames,
      datasets: [{
        label:           "Unidades vendidas",
        data:            window.DASHBOARD.topSales,
        backgroundColor: [gold, accent, success, info, purple],
        borderRadius:    6,
        borderSkipped:   false,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.05)" } },
        x: { grid: { display: false } }
      }
    }
  });
}