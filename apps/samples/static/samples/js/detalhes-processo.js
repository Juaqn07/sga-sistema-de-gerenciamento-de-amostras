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
