// Draw every <canvas data-chart="..."> with Chart.js. The data comes from a widget.
function drawCharts(root) {
  root.querySelectorAll("canvas[data-chart]").forEach((canvas) => {
    if (canvas.dataset.drawn) return;
    canvas.dataset.drawn = "1";
    const spec = JSON.parse(canvas.dataset.chart);
    const style = getComputedStyle(document.documentElement);
    const colors = [style.getPropertyValue("--accent").trim(), style.getPropertyValue("--warn").trim()];
    Chart.defaults.color = style.getPropertyValue("--muted").trim();
    new Chart(canvas, {
      type: spec.kind,
      data: {
        labels: spec.labels,
        datasets: spec.series.map((s, i) => ({
          label: s.label, data: s.data,
          backgroundColor: colors[i % colors.length], borderColor: colors[i % colors.length],
          tension: 0.25,
        })),
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: spec.series.length > 1 } },
        scales: { y: { beginAtZero: true, max: spec.unit === "%" ? 100 : undefined } },
      },
    });
  });
}
// Class map: sort the students and choose what the colour of a cell means.
document.addEventListener("click", (e) => {
  const button = e.target.closest("[data-cm]");
  if (!button) return;
  const card = button.closest(".widget"), table = card.querySelector("table.cm");
  const [what, value] = button.dataset.cm.split(":");
  button.parentElement.querySelectorAll("button").forEach((b) => {
    b.classList.toggle("on", b === button);
    b.setAttribute("aria-pressed", b === button);
  });
  if (what === "colour") {
    table.classList.toggle("gap", value === "gap");
    table.classList.toggle("score", value === "score");
    card.querySelectorAll("[data-colour-key]").forEach((k) => { k.hidden = k.dataset.colourKey !== value; });
  } else {
    const body = table.tBodies[0];
    [...body.rows]
      .sort((a, b) => value === "name" ? a.dataset.name.localeCompare(b.dataset.name) : a.dataset.pct - b.dataset.pct)
      .forEach((row) => body.append(row));
  }
});
document.addEventListener("DOMContentLoaded", () => drawCharts(document));
document.addEventListener("htmx:afterSwap", (e) => drawCharts(e.target));
