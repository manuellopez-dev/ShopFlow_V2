const primary = "#2563eb";
const success = "#059669";
const info    = "#0284c7";
const purple  = "#7c3aed";
const gold    = "#d97706";

// ─── Ventas 7 días ────────────────────────────────────
if (document.getElementById("salesChart")) {
  const ctx = document.getElementById("salesChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels:   window.VENDOR.dayLabels,
      datasets: [{
        label:                "Ventas ($)",
        data:                 window.VENDOR.salesByDay,
        borderColor:          primary,
        backgroundColor:      "rgba(37,99,235,0.1)",
        borderWidth:          2.5,
        pointBackgroundColor: primary,
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

// ─── Top productos ────────────────────────────────────
if (document.getElementById("topChart")) {
  const ctx = document.getElementById("topChart").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels:   window.VENDOR.topNames,
      datasets: [{
        data:            window.VENDOR.topSales,
        backgroundColor: [primary, success, info, purple, gold],
        borderWidth:     2,
        borderColor:     "#fff",
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { font: { family: "Inter" }, boxWidth: 12 } }
      },
      cutout: "60%",
    }
  });
}