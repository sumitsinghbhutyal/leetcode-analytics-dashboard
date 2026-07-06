document.addEventListener("DOMContentLoaded", async () => {
  const difficultyEl = document.getElementById("difficultyChart");
  const activityEl = document.getElementById("activityChart");

  if (difficultyEl) {
    const res = await fetch("/api/difficulty-distribution");
    if (res.ok) {
      const data = await res.json();
      if (!data.error) {
        new Chart(difficultyEl, {
          type: "doughnut",
          data: {
            labels: data.labels,
            datasets: [
              {
                data: data.values,
                backgroundColor: ["#22c55e", "#6366f1", "#f97316"],
              },
            ],
          },
          options: {
            plugins: {
              legend: {
                labels: { color: "#e5e7eb" },
              },
            },
          },
        });
      }
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
              backgroundColor: "#6366f1",
            },
          ],
        },
        options: {
          scales: {
            x: {
              ticks: { color: "#9ca3af" },
            },
            y: {
              ticks: { color: "#9ca3af" },
            },
          },
          plugins: {
            legend: {
              labels: { color: "#e5e7eb" },
            },
          },
        },
      });
    }
  }
});
