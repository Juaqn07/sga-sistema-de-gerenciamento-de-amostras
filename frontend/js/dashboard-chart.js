document.addEventListener("DOMContentLoaded", function () {
  const labels = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"];
  const dataValues = [14, 18, 15, 22, 20, 17];
  const backgroundColors = [
    "rgba(242, 164, 46, 0.7)", // Sem 1 (Laranja)
    "rgba(46, 196, 182, 0.7)", // Sem 2 (Verde-água)
    "rgba(137, 85, 201, 0.7)", // Sem 3 (Roxo)
    "rgba(0, 123, 255, 0.7)",  // Sem 4 (Azul)
    "rgba(232, 99, 132, 0.7)", // Sem 5 (Rosa)
    "rgba(201, 153, 224, 0.7)", // Sem 6 (Lilás)
  ];
  const borderColors = [
    "rgba(242, 164, 46, 1)",
    "rgba(46, 196, 182, 1)",
    "rgba(137, 85, 201, 1)",
    "rgba(0, 123, 255, 1)",
    "rgba(232, 99, 132, 1)",
    "rgba(201, 153, 224, 1)",
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