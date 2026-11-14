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
document.addEventListener("DOMContentLoaded", () => drawCharts(document));
document.addEventListener("htmx:afterSwap", (e) => drawCharts(e.target));
