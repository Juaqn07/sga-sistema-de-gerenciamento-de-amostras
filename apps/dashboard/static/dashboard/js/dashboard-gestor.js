/**
 * Script responsável pelos gráficos do Dashboard do Gestor.
 * Utiliza a biblioteca Chart.js.
 * * Os dados (labels, values, colors) são injetados no HTML pelo Django
 * via tags <script type="application/json"> e recuperados aqui.
 */

document.addEventListener("DOMContentLoaded", function () {
  // =========================================================
  // 1. RECUPERAÇÃO DE DADOS DO DOM
  // =========================================================
  // Elementos ocultos no template contêm os JSONs gerados na View

  const elStatusLabels = document.getElementById("statusLabels");
  const elStatusData = document.getElementById("statusData");
  const elStatusColors = document.getElementById("statusColors");
  const elWeeklyLabels = document.getElementById("weeklyLabels");
  const elWeeklyData = document.getElementById("weeklyData");

  // Verifica se estamos na tela de Gestor (se os elementos existem)
  if (!elStatusLabels || !elWeeklyLabels) return;

  // Parsing seguro dos dados
  const statusLabels = JSON.parse(elStatusLabels.textContent);
  const statusData = JSON.parse(elStatusData.textContent);
  const statusColors = JSON.parse(elStatusColors.textContent);
  const weeklyLabels = JSON.parse(elWeeklyLabels.textContent);
  const weeklyData = JSON.parse(elWeeklyData.textContent);

  // =========================================================
  // 2. GRÁFICO DE STATUS (ROSQUINHA / DOUGHNUT)
  // =========================================================
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
            borderWidth: 0, // Remove borda para visual mais limpo
            hoverOffset: 5, // Efeito de destaque ao passar o mouse
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "75%", // Define a espessura da rosquinha (mais fina)
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 10, // Quadrado da cor menor
              usePointStyle: true, // Usa círculo em vez de quadrado
              padding: 15,
              font: { size: 11 },
            },
          },
        },
      },
    });
  }

  // =========================================================
  // 3. GRÁFICO SEMANAL (BARRAS / BAR)
  // =========================================================
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
            backgroundColor: "#0d6efd", // Azul Primary do Bootstrap
            borderRadius: 4, // Bordas arredondadas no topo da barra
            barThickness: 20, // Largura fixa para elegância
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }, // Oculta legenda (dado único)
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              borderDash: [2, 4], // Linha pontilhada
              color: "#e9ecef", // Cinza bem claro
            },
            ticks: { stepSize: 1 }, // Força números inteiros no eixo Y
          },
          x: {
            grid: { display: false }, // Remove grades verticais
          },
        },
      },
    });
  }
});
