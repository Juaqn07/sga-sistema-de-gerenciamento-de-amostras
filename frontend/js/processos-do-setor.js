/* =================================================== */
/* ===== JAVASCRIPT DA PÁGINA PROCESSOS DO SETOR ===== */
/* (Controla os 4 modais dinâmicos)                  */
/* =================================================== */

document.addEventListener("DOMContentLoaded", function () {
  // Pega a referência de TODOS os modais
  var modalAlterarStatus = document.getElementById("modalAlterarStatus");
  var modalCodigoRastreio = document.getElementById("modalCodigoRastreio");
  var modalAddComentario = document.getElementById("modalAddComentario");
  var modalEncaminharProcesso = document.getElementById(
    "modalEncaminharProcesso"
  );

  // Função "Mestre" que lida com a abertura de qualquer modal
  function handleModalOpen(event) {
    // 'event.relatedTarget' é o ícone que foi clicado
    var button = event.relatedTarget;
    // 'event.target' é o modal que está sendo aberto
    var modal = event.target;

    // Pega os dados comuns (que todos os ícones têm)
    var processoId = button.getAttribute("data-processo-id");
    var processoTitulo = button.getAttribute("data-processo-titulo");
    var infoText = processoId + " - " + processoTitulo;

    // Verifica qual modal está sendo aberto e age de acordo
    if (modal.id === "modalAlterarStatus") {
      var processoStatus = button.getAttribute("data-processo-status");
      var modalInfo = modal.querySelector("#modalProcessoInfo");
      var modalSelect = modal.querySelector("#modalSelectStatus");

      modalInfo.textContent = infoText;
      modalSelect.value = processoStatus;
    } else if (modal.id === "modalCodigoRastreio") {
      var processoRastreio = button.getAttribute("data-processo-rastreio");
      var modalInfo = modal.querySelector("#modalRastreioInfo");
      var modalInput = modal.querySelector("#modalRastreioInput");

      modalInfo.textContent = infoText;
      modalInput.value = processoRastreio || ""; // Usa o código ou deixa em branco
    } else if (modal.id === "modalAddComentario") {
      var modalInfo = modal.querySelector("#modalComentarioInfo");
      var modalTextarea = modal.querySelector("#modalComentarioTextarea");

      modalInfo.textContent = infoText;
      modalTextarea.value = ""; // Limpa comentários anteriores
    } else if (modal.id === "modalEncaminharProcesso") {
      var modalInfo = modal.querySelector("#modalEncaminharInfo");
      var radioPadrao = modal.querySelector("#fluxoPadrao");

      modalInfo.textContent = infoText;
      radioPadrao.checked = true; // Sempre reseta para "Fluxo Padrão"
    }
  }

  // Adiciona o "ouvinte" para CADA modal
  if (modalAlterarStatus)
    modalAlterarStatus.addEventListener("show.bs.modal", handleModalOpen);
  if (modalCodigoRastreio)
    modalCodigoRastreio.addEventListener("show.bs.modal", handleModalOpen);
  if (modalAddComentario)
    modalAddComentario.addEventListener("show.bs.modal", handleModalOpen);
  if (modalEncaminharProcesso)
    modalEncaminharProcesso.addEventListener("show.bs.modal", handleModalOpen);
});
