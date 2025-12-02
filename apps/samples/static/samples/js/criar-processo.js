/**
 * Script responsável pela página "Criar Processo".
 * Gerencia: Busca de Clientes, Modais de Criação/Edição e Lógica de Formulário.
 */

// Variável Global: Armazena o objeto do cliente selecionado para permitir edição imediata
let clienteAtualObj = null;

document.addEventListener("DOMContentLoaded", function () {
  // Elementos principais do DOM
  const btnSearch = document.getElementById("btn-search");
  const btnSalvarNovo = document.getElementById("btn-salvar-novo");
  const btnEditarCliente = document.getElementById("btn-editar-cliente");
  const btnSalvarEdicao = document.getElementById("btn-salvar-edicao");

  // Helper para CSRF Token (Segurança Django)
  const getCsrfToken = () =>
    document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

  // =========================================================
  // 1. BUSCA DE CLIENTES (AUTOCOMPLETE)
  // =========================================================
  if (btnSearch) {
    btnSearch.addEventListener("click", function () {
      const term = document.getElementById("cliente-search").value;
      const searchUrl = btnSearch.getAttribute("data-url"); // URL definida no HTML

      if (term.length < 2) return; // Evita buscas muito curtas

      fetch(`${searchUrl}?term=${term}`)
        .then((res) => res.json())
        .then((data) => {
          const resultsDiv = document.getElementById("search-results");
          resultsDiv.innerHTML = "";
          resultsDiv.classList.remove("d-none");

          if (data.results.length === 0) {
            resultsDiv.innerHTML =
              '<div class="list-group-item">Nenhum cliente encontrado.</div>';
            return;
          }

          // Renderiza lista de resultados de forma SEGURA (Sem innerHTML)
          data.results.forEach((cliente) => {
            const item = document.createElement("a");
            item.className =
              "list-group-item list-group-item-action result-item";

            // Criação segura dos elementos de texto
            const nomeStrong = document.createElement("strong");
            nomeStrong.textContent = cliente.nome; // Sanitização automática

            const localSmall = document.createElement("small");
            // Adiciona espaço antes do parênteses para estética
            localSmall.textContent = ` (${cliente.cidade}/${cliente.estado})`;

            // Montagem do elemento
            item.appendChild(nomeStrong);
            item.appendChild(localSmall);

            // Ao clicar, seleciona o cliente e esconde a busca
            item.onclick = () => selecionarCliente(cliente);

            resultsDiv.appendChild(item);
          });
        });
    });
  }

  // =========================================================
  // 2. MODAL: SALVAR NOVO CLIENTE
  // =========================================================
  if (btnSalvarNovo) {
    btnSalvarNovo.addEventListener("click", function () {
      const form = document.getElementById("formNovoCliente");
      const createUrl = btnSalvarNovo.getAttribute("data-url");

      // Validação: Impede envio se CEP estiver inválido ou campos vazios
      const cepInput = form.querySelector('input[name="cep"]');
      if (cepInput && cepInput.classList.contains("is-invalid")) {
        alert("CEP Inválido. Corrija para prosseguir.");
        return;
      }
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      // UX: Feedback visual no botão
      const originalText = this.innerHTML;
      this.innerHTML =
        '<span class="spinner-border spinner-border-sm"></span> Salvando...';
      this.disabled = true;

      // Envio AJAX
      const formData = new FormData(form);
      const payload = Object.fromEntries(formData.entries());

      fetch(createUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(payload),
      })
        .then((r) => r.json())
        .then((result) => {
          this.innerHTML = originalText;
          this.disabled = false;

          if (result.status === "success") {
            // Sucesso: Fecha modal, seleciona cliente e limpa form
            bootstrap.Modal.getInstance(
              document.getElementById("modalNovoCliente")
            ).hide();
            selecionarCliente(result.cliente);
            form.reset();
            form
              .querySelectorAll(".is-valid, .is-invalid")
              .forEach((el) => el.classList.remove("is-valid", "is-invalid"));
            form.querySelector(".cep-status").innerHTML = "";
          } else {
            alert("Erro: " + result.message);
          }
        })
        .catch(() => {
          this.innerHTML = originalText;
          this.disabled = false;
          alert("Erro de comunicação com o servidor.");
        });
    });
  }

  // =========================================================
  // 3. EDITAR CLIENTE SELECIONADO
  // =========================================================

  // Abre o modal preenchendo os dados
  if (btnEditarCliente) {
    btnEditarCliente.addEventListener("click", function () {
      if (!clienteAtualObj) return;

      // Preenche os campos do modal de edição com os dados da memória
      const fields = [
        "id",
        "nome",
        "responsavel",
        "cep",
        "logradouro",
        "numero",
        "bairro",
        "complemento",
        "cidade",
        "estado",
      ];
      fields.forEach((field) => {
        const el = document.getElementById(`edit-${field}`);
        if (el) el.value = clienteAtualObj[field] || "";
      });

      new bootstrap.Modal(document.getElementById("modalEditarCliente")).show();
    });
  }

  // Salva a edição
  if (btnSalvarEdicao) {
    btnSalvarEdicao.addEventListener("click", function () {
      const form = document.getElementById("formEditarCliente");
      const id = document.getElementById("edit-id").value;
      const editUrl = `/processos/api/editar-cliente/${id}/`;

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const formData = new FormData(form);

      fetch(editUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(Object.fromEntries(formData.entries())),
      })
        .then((r) => r.json())
        .then((result) => {
          if (result.status === "success") {
            bootstrap.Modal.getInstance(
              document.getElementById("modalEditarCliente")
            ).hide();
            // Atualiza a visualização do card com os novos dados
            selecionarCliente(result.cliente);
          } else {
            alert("Erro ao editar: " + result.message);
          }
        });
    });
  }

  // =========================================================
  // 4. INTEGRAÇÃO COM BUSCA-CEP.JS
  // =========================================================
  // Verifica se a função existe antes de chamar
  if (typeof setupCepAutocomplete === "function") {
    // Mapeamento para o Modal Novo
    setupCepAutocomplete(
      '#formNovoCliente input[name="cep"]',
      {
        logradouro: '#formNovoCliente input[name="logradouro"]',
        bairro: '#formNovoCliente input[name="bairro"]',
        cidade: '#formNovoCliente input[name="cidade"]',
        estado: '#formNovoCliente input[name="estado"]',
        numero: '#formNovoCliente input[name="numero"]',
      },
      "#btn-salvar-novo"
    );

    // Mapeamento para o Modal Editar
    setupCepAutocomplete(
      '#formEditarCliente input[name="cep"]',
      {
        logradouro: '#formEditarCliente input[name="logradouro"]',
        bairro: '#formEditarCliente input[name="bairro"]',
        cidade: '#formEditarCliente input[name="cidade"]',
        estado: '#formEditarCliente input[name="estado"]',
        numero: '#formEditarCliente input[name="numero"]',
      },
      "#btn-salvar-edicao"
    );
  }

  // =========================================================
  // 5. UX: CAMPO CONDICIONAL (TIPO TRANSPORTE)
  // =========================================================
  const selectTransporte = document.getElementById("id_tipo_transporte");
  const divCodigoCarga = document.getElementById("divCodigoCarga");

  if (selectTransporte && divCodigoCarga) {
    function checkTransporte() {
      // Exibe campo extra apenas se for 'Carga'
      const isCarga = selectTransporte.value === "carga";
      divCodigoCarga.style.display = isCarga ? "block" : "none";

      // Limpa valor se esconder para evitar envio de dados sujos
      if (!isCarga) {
        const input = divCodigoCarga.querySelector("input");
        if (input) input.value = "";
      }
    }
    selectTransporte.addEventListener("change", checkTransporte);
    checkTransporte(); // Inicialização
  }
});

// --- FUNÇÕES AUXILIARES GLOBAIS ---

/**
 * Atualiza a interface com os dados do cliente selecionado.
 * Esconde a área de busca e mostra o card de resumo.
 * @param {object} cliente - Objeto cliente retornado pela API.
 */
function selecionarCliente(cliente) {
  clienteAtualObj = cliente; // Persiste globalmente

  // Alterna visibilidade
  document.getElementById("area-busca").classList.add("d-none");
  document
    .getElementById("card-cliente-selecionado")
    .classList.remove("d-none");

  // Preenche Card
  document.getElementById("card-nome").innerText = cliente.nome;
  document.getElementById("card-ac").innerText = cliente.responsavel;

  const endereco =
    cliente.endereco_completo ||
    `${cliente.logradouro}, ${cliente.numero} - ${cliente.cidade}/${cliente.estado}`;
  document.getElementById("card-endereco").innerText = endereco;
  document.getElementById("card-cep").innerText = cliente.cep;

  // Preenche Input Oculto (CRÍTICO: Isso é o que o Django recebe no POST)
  document.getElementById("selected_cliente_id").value = cliente.id;
}

function limparCliente() {
  clienteAtualObj = null;
  document.getElementById("area-busca").classList.remove("d-none");
  document.getElementById("card-cliente-selecionado").classList.add("d-none");
  document.getElementById("selected_cliente_id").value = "";
  document.getElementById("cliente-search").value = "";
  document.getElementById("search-results").classList.add("d-none");
}
