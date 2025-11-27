document.addEventListener("DOMContentLoaded", function () {
  // --- GRÁFICO DE STATUS (ROSQUINHA) ---
  const statusLabels = JSON.parse(
    document.getElementById("statusLabels").textContent
  );
  const statusData = JSON.parse(
    document.getElementById("statusData").textContent
  );
  const statusColors = JSON.parse(
    document.getElementById("statusColors").textContent
  );

  const ctxStatus = document.getElementById("chartStatus");
  if (ctxStatus) {
    new Chart(ctxStatus, {
      type: "doughnut",
      data: {
        labels: statusLabels,
        datasets: [
          {
            data: statusData,
            backgroundColor: statusColors,
            borderWidth: 0,
            hoverOffset: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 10,
              usePointStyle: true,
              padding: 15,
              font: { size: 11 },
            },
          },
        },
        cutout: "75%", // Rosquinha fina e elegante
      },
    });
  }

  // --- GRÁFICO SEMANAL (BARRAS) ---
  const weeklyLabels = JSON.parse(
    document.getElementById("weeklyLabels").textContent
  );
  const weeklyData = JSON.parse(
    document.getElementById("weeklyData").textContent
  );

  const ctxWeekly = document.getElementById("chartWeekly");
  if (ctxWeekly) {
    new Chart(ctxWeekly, {
      type: "bar",
      data: {
        labels: weeklyLabels,
        datasets: [
          {
            label: "Novos Processos",
            data: weeklyData,
            backgroundColor: "#0d6efd", // Azul Bootstrap
            borderRadius: 4,
            barThickness: 20, // Barras mais finas e elegantes
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }, // Não precisa de legenda para 1 série
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { borderDash: [2, 4], color: "#e9ecef" }, // Grid tracejado sutil
            ticks: { stepSize: 1 }, // Números inteiros
          },
          x: {
            grid: { display: false }, // Remove grid vertical
          },
        },
      },
    });
  }
});
