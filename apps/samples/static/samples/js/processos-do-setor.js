/* =================================================== */
/* JAVASCRIPT DA PÁGINA PROCESSOS DO SETOR             */
/* =================================================== */

// Variável para guardar o ID do processo que está no modal aberto
let processoPkAtual = null;

document.addEventListener("DOMContentLoaded", function () {
  // Função para pegar CSRF
  function getCsrfToken() {
    // Tenta pegar do input (se houver form na página) ou cookie
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input) return input.value;
    return "";
  }

  // Função Genérica de Fetch
  function sendData(url, data) {
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(data),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.status === "success") {
          // Recarrega a página para mostrar o novo status/rastreio
          window.location.reload();
        } else {
          alert("Erro: " + (result.message || "Erro desconhecido"));
        }
      })
      .catch((err) => console.error(err));
  }

  // --- LÓGICA DE ABERTURA DOS MODAIS (Preencher dados) ---
  const modais = document.querySelectorAll(".modal");
  modais.forEach((modalEl) => {
    modalEl.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return; // Se foi aberto via JS, ignora

      // Pega os dados do botão
      const pk = button.getAttribute("data-processo-pk");
      const codigo = button.getAttribute("data-processo-id");
      const titulo = button.getAttribute("data-processo-titulo");

      // Salva PK globalmente
      processoPkAtual = pk;

      // Atualiza Título do Modal
      const infoText = `${codigo} - ${titulo}`;

      // Lógica específica de cada modal
      if (modalEl.id === "modalAlterarStatus") {
        modalEl.querySelector("#modalProcessoInfo").textContent = infoText;
        const statusAtual = button.getAttribute("data-processo-status");
        modalEl.querySelector("#modalSelectStatus").value = statusAtual;
      } else if (modalEl.id === "modalCodigoRastreio") {
        modalEl.querySelector("#modalRastreioInfo").textContent = infoText;
        const rastreioAtual = button.getAttribute("data-processo-rastreio");
        modalEl.querySelector("#modalRastreioInput").value =
          rastreioAtual || "";
      } else if (modalEl.id === "modalAddComentario") {
        modalEl.querySelector("#modalComentarioInfo").textContent = infoText;
        modalEl.querySelector("#modalComentarioTextarea").value = "";
        modalEl.querySelector("#fluxoGestao").checked = false;
      }
    });
  });

  // --- LISTENERS DOS BOTÕES DE SALVAR ---

  // 1. Salvar Status
  const btnStatus = document.getElementById("btnSalvarStatus");
  if (btnStatus) {
    btnStatus.addEventListener("click", function () {
      const novoStatus = document.getElementById("modalSelectStatus").value;
      const url = `/processos/api/processo/${processoPkAtual}/status/`;
      sendData(url, { status: novoStatus });
    });
  }

  // 2. Salvar Rastreio
  const btnRastreio = document.getElementById("btnSalvarRastreio");
  if (btnRastreio) {
    btnRastreio.addEventListener("click", function () {
      const codigo = document.getElementById("modalRastreioInput").value;
      const url = `/processos/api/processo/${processoPkAtual}/rastreio/`;
      sendData(url, { codigo_rastreio: codigo });
    });
  }

  // 3. Salvar Comentário
  const btnComentario = document.getElementById("btnSalvarComentario");
  if (btnComentario) {
    btnComentario.addEventListener("click", function () {
      const texto = document.getElementById("modalComentarioTextarea").value;
      const gestao = document.getElementById("fluxoGestao").checked;
      const url = `/processos/api/processo/${processoPkAtual}/comentario/`;
      sendData(url, { texto: texto, encaminhar_gestao: gestao });
    });
  }
});

function atribuirProcesso(pk) {
  if (!confirm("Deseja assumir a responsabilidade por este processo?")) return;

  // Pega o token (reutilizando a função que já existe ou criando uma nova instância)
  const token = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(`/processos/api/processo/${pk}/atribuir/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
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

function toggleCancelar(pk, acao) {
  const mensagem =
    acao === "cancelar"
      ? "Tem certeza que deseja CANCELAR este processo?\n\nNinguém poderá mais alterá-lo ou adicionar anexos."
      : "Deseja REATIVAR este processo?\n\nEle voltará para a fila 'Não Atribuído' e ficará disponível para separação.";

  if (!confirm(mensagem)) return;

  const token = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(`/processos/api/processo/${pk}/cancelar/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
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
