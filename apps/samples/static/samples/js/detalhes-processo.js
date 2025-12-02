/**
 * Script responsável pela página de Detalhes do Processo.
 * Gerencia:
 * 1. Abertura automática da aba correta (via URL).
 * 2. Lógica AJAX para o botão "Atualizar Rastreio".
 */

document.addEventListener("DOMContentLoaded", function () {
  // =========================================================
  // 1. GERENCIAMENTO DE ABAS (DEEPLINKING)
  // =========================================================
  // Permite abrir a página direto na aba 'Timeline' usando ?tab=timeline na URL
  const urlParams = new URLSearchParams(window.location.search);
  const activeTabName = urlParams.get("tab");

  if (activeTabName === "timeline") {
    const tabButton = document.querySelector("#timeline-tab");
    if (tabButton) {
      const tabInstance = new bootstrap.Tab(tabButton);
      tabInstance.show();
      // Rola a tela suavemente até a aba
      tabButton.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  // =========================================================
  // 2. ATUALIZAÇÃO DE RASTREIO (AJAX)
  // =========================================================
  const btnUpdateTracking = document.getElementById("btn-update-tracking");

  if (btnUpdateTracking) {
    btnUpdateTracking.addEventListener("click", function (event) {
      event.preventDefault(); // Impede o link padrão de navegar

      const targetUrl = this.getAttribute("href");
      const originalBtnContent = this.innerHTML;

      // UX: Feedback Visual de Carregamento
      this.innerHTML =
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verificando...';
      this.classList.add("disabled");

      // Recupera o Token CSRF para segurança do Django
      const csrfToken =
        document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

      // Executa a chamada API
      fetch(targetUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({}), // Corpo vazio, pois a URL já contém o ID
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // Sucesso: Recarrega a página forçando a aba Timeline
            const currentPath = window.location.pathname;
            window.location.href = `${currentPath}?tab=timeline`;
          } else if (data.status === "info") {
            // Info: Apenas avisa que não houve mudança
            alert(data.message);
            resetButton(this, originalBtnContent);
          } else {
            // Erro Lógico (ex: Processo cancelado)
            alert("Aviso: " + data.message);
            resetButton(this, originalBtnContent);
          }
        })
        .catch((error) => {
          console.error("Erro na requisição:", error);
          alert("Erro de conexão ao tentar atualizar os Correios.");
          resetButton(this, originalBtnContent);
        });
    });
  }

  /**
   * Restaura o estado original do botão após a requisição.
   */
  function resetButton(buttonElement, originalContent) {
    buttonElement.innerHTML = originalContent;
    buttonElement.classList.remove("disabled");
  }
});
// =========================================================
// 3. COTAÇÃO DE FRETE (CORREIOS)
// =========================================================
const btnCotacao = document.getElementById("btnRealizarCotacao");

if (btnCotacao) {
  btnCotacao.addEventListener("click", function () {
    const modalBody = document.querySelector("#modalCotacao .modal-body");
    const feedbackDiv = document.getElementById("resultadoCotacao");
    const loadingDiv = document.getElementById("loadingCotacao");
    const tableBody = document.getElementById("tabelaResultados");

    // 1. Coleta de Dados do Formulário
    const formato = document.getElementById("cotacaoFormato").value;
    const peso = document.getElementById("cotacaoPeso").value;
    const valor = document.getElementById("cotacaoValor").value;

    // Seletores de dimensão (podem não existir se a lógica de esconder for implementada)
    const compInput = document.querySelector('input[name="comp"]');
    const altInput = document.querySelector('input[name="alt"]');
    const largInput = document.querySelector('input[name="larg"]');

    const comp = compInput ? compInput.value : "0";
    const alt = altInput ? altInput.value : "0";
    const larg = largInput ? largInput.value : "0";

    // 2. Validação (Frontend)
    if (!peso || parseFloat(peso) <= 0) {
      alert("Por favor, informe o peso do objeto.");
      return;
    }

    // Validação de Dimensões (apenas se não for envelope, ou regra específica)
    if (formato !== "3") {
      // 3 = Envelope
      if (!comp || !alt || !larg || comp == "0" || alt == "0" || larg == "0") {
        alert(
          "Para caixas e rolos, as dimensões (C x A x L) são obrigatórias."
        );
        return;
      }
    }

    // 3. Preparação da UI
    feedbackDiv.classList.add("d-none");
    loadingDiv.classList.remove("d-none");
    this.disabled = true; // Evita duplo clique

    // Recupera ID do processo da URL ou de um atributo (assumindo que estamos na pag de detalhes)
    // O botão que abre o modal deve ter o ID, ou pegamos da URL atual
    // Vamos pegar da URL atual que tem o ID: /processos/123/
    const pathParts = window.location.pathname.split("/");
    // Filtra vazios e pega o último segmento numérico
    const processoId = pathParts.filter((p) => !isNaN(p) && p !== "").pop();

    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    // 4. Requisição AJAX
    fetch(`/correios/api/cotacao/${processoId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        formato: formato,
        peso: peso, // Em gramas (API espera string ou int)
        valor_declarado: valor,
        comprimento: comp,
        altura: alt,
        largura: larg,
      }),
    })
      .then((response) => response.json())
      .then((result) => {
        loadingDiv.classList.add("d-none");
        this.disabled = false;

        if (result.status === "success") {
          // Limpa tabela antiga
          tableBody.innerHTML = "";

          // Popula novos resultados
          result.data.forEach((servico) => {
            const row = document.createElement("tr");

            // Lógica de cor para o prazo (Destaque visual)
            const prazoTexto =
              servico.prazo === "1"
                ? "1 dia útil"
                : `${servico.prazo} dias úteis`;

            row.innerHTML = `
                <td class="fw-bold text-start">${servico.servico}</td>
                <td>${prazoTexto}</td>
                <td class="text-success fw-bold">R$ ${servico.preco}</td>
                <td class="small text-muted">${
                  servico.entrega_prevista || "-"
                }</td>
              `;
            tableBody.appendChild(row);
          });

          feedbackDiv.classList.remove("d-none");
        } else {
          alert("Erro na cotação: " + result.message);
        }
      })
      .catch((err) => {
        console.error(err);
        loadingDiv.classList.add("d-none");
        this.disabled = false;
        alert("Erro de comunicação com o servidor.");
      });
  });
}
