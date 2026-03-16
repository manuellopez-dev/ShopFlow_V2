// ─── Configuración de Partículas ─────────────────────
if (document.getElementById("particles-js")) {
  particlesJS("particles-js", {
    particles: {
      number:   { value: 40, density: { enable: true, value_area: 800 } },
      color:    { value: "#c9a96e" },
      shape:    { type: "circle" },
      opacity:  { value: 0.3, random: true },
      size:     { value: 3, random: true },
      line_linked: {
        enable:   true,
        distance: 150,
        color:    "#c9a96e",
        opacity:  0.15,
        width:    1
      },
      move: {
        enable:   true,
        speed:    1.5,
        random:   true,
        out_mode: "out"
      }
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: { enable: true, mode: "repulse" },
        onclick: { enable: true, mode: "push" }
      },
      modes: {
        repulse: { distance: 80 },
        push:    { particles_nb: 3 }
      }
    }
  });
}