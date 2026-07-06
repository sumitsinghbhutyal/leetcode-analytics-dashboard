document.addEventListener("DOMContentLoaded", async () => {
  const contestEl = document.getElementById("contestChart");
  const activityEl = document.getElementById("activityChartAnalytics");

  if (contestEl) {
    const res = await fetch("/api/contest-history");
    if (res.ok) {
      const data = await res.json();
      new Chart(contestEl, {
        type: "line",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Rating",
              data: data.ratings,
              borderColor: "#6366f1",
              backgroundColor: "rgba(99, 102, 241, 0.15)",
              fill: true,
              tension: 0.2,
            },
          ],
        },
        options: {
          scales: {
            x: { ticks: { color: "#9ca3af" } },
            y: { ticks: { color: "#9ca3af" } },
          },
          plugins: {
            legend: { labels: { color: "#e5e7eb" } },
          },
        },
      });
    }
  }

  if (activityEl) {
    const res = await fetch("/api/activity");
    if (res.ok) {
      const data = await res.json();
      new Chart(activityEl, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Problems Solved",
              data: data.values,
              backgroundColor: "#22c55e",
            },
          ],
        },
        options: {
          scales: {
            x: { ticks: { color: "#9ca3af" } },
            y: { ticks: { color: "#9ca3af" } },
          },
          plugins: {
            legend: { labels: { color: "#e5e7eb" } },
          },
        },
      });
    }
  }
});
