document.addEventListener("DOMContentLoaded", function () {
  
  // 1. Lendo os dados que o Django "imprimiu" no HTML
  const labels = JSON.parse(document.getElementById('chartLabels').textContent);
  const dataValues = JSON.parse(document.getElementById('chartData').textContent);

  // 2. O resto do seu código (cores, etc.)
  const backgroundColors = [
    'hsla(238, 82%, 15%, 0.8)',
    'hsla(238, 82%, 15%, 0.8)',
    'hsla(238, 82%, 15%, 0.8)',
    'hsla(238, 82%, 15%, 0.8)',
  ];
  const borderColors = [
    "hsla(238, 93.00%, 27.80%, 0.60)",
    "hsla(238, 93.00%, 27.80%, 0.60)",
    "hsla(238, 93.00%, 27.80%, 0.60)",
    "hsla(238, 93.00%, 27.80%, 0.60)",
    "hsla(238, 93.00%, 27.80%, 0.60)",
    "hsla(238, 93.00%, 27.80%, 0.60)",
  ];

  const ctx = document.getElementById("weeklyProcessChart").getContext("2d");
  
  // 3. Renderizando o gráfico com os dados dinâmicos
  const weeklyProcessChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels, // <-- Vindo do Django
      datasets: [
        {
          label: "Processos",
          data: dataValues, // <-- Vindo do Django
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1,
          borderRadius: 4, 
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 7,
          },
        },
      },
    },
  });
});