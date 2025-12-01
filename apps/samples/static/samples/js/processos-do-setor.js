/**
 * Script principal do Dashboard (Lista de Processos).
 * Gerencia:
 * 1. Modais de ação (Status, Rastreio, Comentário).
 * 2. Funções globais de ação (Atribuir, Cancelar).
 * 3. Comunicação AJAX com as APIs do backend.
 */

// Variável Global: Armazena o ID do processo que está sendo manipulado no modal aberto.
let processoIdSelecionado = null;

document.addEventListener("DOMContentLoaded", function () {
  // --- HELPER: Obtém o Token CSRF do Django ---
  function getCsrfToken() {
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  // --- HELPER: Envio Genérico de Dados (AJAX) ---
  function sendApiRequest(url, payload) {
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          // Sucesso: Recarrega a página para refletir mudanças
          window.location.reload();
        } else {
          alert("Erro: " + (result.message || "Ocorreu um erro desconhecido."));
        }
      })
      .catch((err) => {
        console.error("Erro de rede:", err);
        alert("Erro de comunicação com o servidor.");
      });
  }

  // =========================================================
  // 1. CONFIGURAÇÃO DOS MODAIS (EVENTO 'SHOW')
  // =========================================================
  // Preenche os dados dentro do modal antes dele aparecer na tela
  const modais = document.querySelectorAll(".modal");

  modais.forEach((modalEl) => {
    modalEl.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botão que acionou o modal
      if (!button) return;

      // Extrai dados dos atributos data-* do botão HTML
      const pk = button.getAttribute("data-processo-pk");
      const codigo = button.getAttribute("data-processo-id");
      const titulo = button.getAttribute("data-processo-titulo");

      // Atualiza a variável global
      processoIdSelecionado = pk;

      // Monta o texto de cabeçalho (Ex: "PRC-2025-001 - Amostra X")
      const infoText = `${codigo} - ${titulo}`;

      // Lógica específica para cada tipo de modal
      if (modalEl.id === "modalAlterarStatus") {
        modalEl.querySelector("#modalProcessoInfo").textContent = infoText;
        // Pré-seleciona o status atual
        const statusAtual = button.getAttribute("data-processo-status");
        modalEl.querySelector("#modalSelectStatus").value = statusAtual;
      } else if (modalEl.id === "modalCodigoRastreio") {
        modalEl.querySelector("#modalRastreioInfo").textContent = infoText;
        // Preenche código atual se existir
        const rastreioAtual = button.getAttribute("data-processo-rastreio");
        modalEl.querySelector("#modalRastreioInput").value =
          rastreioAtual || "";
      } else if (modalEl.id === "modalAddComentario") {
        modalEl.querySelector("#modalComentarioInfo").textContent = infoText;
        // Limpa campos anteriores
        modalEl.querySelector("#modalComentarioTextarea").value = "";
        modalEl.querySelector("#fluxoGestao").checked = false;
      }
    });
  });

  // =========================================================
  // 2. LISTENERS DOS BOTÕES "SALVAR" NOS MODAIS
  // =========================================================

  // A. Salvar Status
  const btnStatus = document.getElementById("btnSalvarStatus");
  if (btnStatus) {
    btnStatus.addEventListener("click", function () {
      const novoStatus = document.getElementById("modalSelectStatus").value;
      const url = `/processos/api/processo/${processoIdSelecionado}/status/`;
      sendApiRequest(url, { status: novoStatus });
    });
  }

  // B. Salvar Rastreio (Carga ou Correios)
  const btnRastreio = document.getElementById("btnSalvarRastreio");
  if (btnRastreio) {
    btnRastreio.addEventListener("click", function () {
      const codigo = document.getElementById("modalRastreioInput").value;
      const url = `/processos/api/processo/${processoIdSelecionado}/rastreio/`;
      sendApiRequest(url, { codigo_rastreio: codigo });
    });
  }

  // C. Salvar Comentário / Ocorrência
  const btnComentario = document.getElementById("btnSalvarComentario");
  if (btnComentario) {
    btnComentario.addEventListener("click", function () {
      const texto = document.getElementById("modalComentarioTextarea").value;
      const encaminharGestao = document.getElementById("fluxoGestao").checked;

      const url = `/processos/api/processo/${processoIdSelecionado}/comentario/`;
      sendApiRequest(url, {
        texto: texto,
        encaminhar_gestao: encaminharGestao,
      });
    });
  }
});

// =========================================================
// 3. FUNÇÕES GLOBAIS (ACIONADAS DIRETAMENTE NO HTML)
// =========================================================

/**
 * Acionado pelo botão "Atribuir a mim".
 * Define o usuário logado como responsável pela separação.
 * @param {number} pk - ID do processo.
 */
function atribuirProcesso(pk) {
  if (!confirm("Deseja assumir a responsabilidade por este processo?")) return;

  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(`/processos/api/processo/${pk}/atribuir/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({}),
  })
    .then((r) => r.json())
    .then((result) => {
      if (result.status === "success") {
        window.location.reload();
      } else {
        alert("Erro ao atribuir: " + result.message);
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Acionado pelos botões de Cancelar ou Reativar.
 * @param {number} pk - ID do processo.
 * @param {string} acao - Tipo de ação: 'cancelar' ou 'reativar'.
 */
function toggleCancelar(pk, acao) {
  let mensagem = "";

  if (acao === "cancelar") {
    mensagem =
      "Tem certeza que deseja CANCELAR este processo?\n\nNinguém poderá mais alterá-lo ou adicionar anexos.";
  } else {
    mensagem =
      "Deseja REATIVAR este processo?\n\nEle voltará para a fila 'Não Atribuído' e ficará disponível para separação.";
  }

  if (!confirm(mensagem)) return;

  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(`/processos/api/processo/${pk}/cancelar/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({}),
  })
    .then((r) => r.json())
    .then((result) => {
      if (result.status === "success") {
        window.location.reload();
      } else {
        alert("Erro: " + result.message);
      }
    })
    .catch((err) => console.error(err));
}
