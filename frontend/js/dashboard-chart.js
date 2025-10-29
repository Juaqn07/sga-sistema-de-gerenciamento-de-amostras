document.addEventListener("DOMContentLoaded", function () {
  const labels = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"];
  const dataValues = [14, 18, 15, 22, 20, 17];
  const backgroundColors = [
    "hsla(238, 93.00%, 27.80%, 0.87)", // Sem 1 (Laranja)
    "hsla(238, 93.00%, 27.80%, 0.87)", // Sem 2 (Verde-água)
    "hsla(238, 93.00%, 27.80%, 0.87)", // Sem 3 (Roxo)
    "hsla(238, 93.00%, 27.80%, 0.87)",  // Sem 4 (Azul)
    "hsla(238, 93.00%, 27.80%, 0.87)", // Sem 5 (Rosa)
    "hsla(238, 93.00%, 27.80%, 0.87)", // Sem 6 (Lilás)
  ];
  const borderColors = [
    "hsla(238, 93.00%, 27.80%, 0.87)",
    "hsla(238, 93.00%, 27.80%, 0.87)",
    "hsla(238, 93.00%, 27.80%, 0.87)",
    "hsla(238, 93.00%, 27.80%, 0.87)",
    "hsla(238, 93.00%, 27.80%, 0.87)",
    "hsla(238, 93.00%, 27.80%, 0.87)",
  ];

  const ctx = document.getElementById("weeklyProcessChart").getContext("2d");
  const weeklyProcessChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Processos",
          data: dataValues,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1,
          borderRadius: 4, // Arredonda o topo das barras
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        // Remove a legenda (não tem na imagem)
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          // Define os "passos" do eixo Y (0, 7, 14, 21, 28) como na imagem
          ticks: {
            stepSize: 7,
          },
        },
      },
    },
  });
});