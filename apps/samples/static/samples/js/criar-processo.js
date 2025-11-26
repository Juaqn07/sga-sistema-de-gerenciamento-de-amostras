// Variável Global para armazenar dados do cliente atual
let clienteAtualObj = null;

document.addEventListener("DOMContentLoaded", function () {
  const btnSearch = document.getElementById("btn-search");
  const btnSalvarNovo = document.getElementById("btn-salvar-novo");
  const btnEditarCliente = document.getElementById("btn-editar-cliente");
  const btnSalvarEdicao = document.getElementById("btn-salvar-edicao");

  function getCsrfToken() {
    const tokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return tokenInput ? tokenInput.value : "";
  }

  // --- BUSCA ---
  if (btnSearch) {
    btnSearch.addEventListener("click", function () {
      const term = document.getElementById("cliente-search").value;
      const searchUrl = btnSearch.getAttribute("data-url");

      if (term.length < 2) return;

      fetch(`${searchUrl}?term=${term}`)
        .then((response) => response.json())
        .then((data) => {
          const resultsDiv = document.getElementById("search-results");
          resultsDiv.innerHTML = "";
          resultsDiv.classList.remove("d-none");

          if (data.results.length === 0) {
            resultsDiv.innerHTML =
              '<div class="list-group-item">Nenhum cliente encontrado.</div>';
            return;
          }

          data.results.forEach((cliente) => {
            const item = document.createElement("a");
            item.className =
              "list-group-item list-group-item-action result-item";
            item.innerHTML = `<strong>${cliente.nome}</strong> <small>(${cliente.cidade}/${cliente.estado})</small>`;
            item.onclick = function () {
              selecionarCliente(cliente);
            };
            resultsDiv.appendChild(item);
          });
        });
    });
  }

  // --- SALVAR NOVO ---
  if (btnSalvarNovo) {
    btnSalvarNovo.addEventListener("click", function () {
      const form = document.getElementById("formNovoCliente");
      const createUrl = btnSalvarNovo.getAttribute("data-url");

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      fetch(createUrl, {
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
            bootstrap.Modal.getInstance(
              document.getElementById("modalNovoCliente")
            ).hide();
            selecionarCliente(result.cliente);
            form.reset(); // Limpa o form para a próxima
          } else {
            alert("Erro: " + result.message);
          }
        });
    });
  }

  // --- ABRIR EDIÇÃO ---
  if (btnEditarCliente) {
    btnEditarCliente.addEventListener("click", function () {
      if (!clienteAtualObj) return;

      // Preenche o formulário de edição com os dados da memória
      document.getElementById("edit-id").value = clienteAtualObj.id;
      document.getElementById("edit-nome").value = clienteAtualObj.nome;
      document.getElementById("edit-responsavel").value =
        clienteAtualObj.responsavel;
      document.getElementById("edit-cep").value = clienteAtualObj.cep || "";
      document.getElementById("edit-logradouro").value =
        clienteAtualObj.logradouro;
      document.getElementById("edit-numero").value = clienteAtualObj.numero;
      document.getElementById("edit-bairro").value = clienteAtualObj.bairro;
      document.getElementById("edit-complemento").value =
        clienteAtualObj.complemento || "";
      document.getElementById("edit-cidade").value = clienteAtualObj.cidade;
      document.getElementById("edit-estado").value = clienteAtualObj.estado;

      // Abre o modal
      const modal = new bootstrap.Modal(
        document.getElementById("modalEditarCliente")
      );
      modal.show();
    });
  }

  // --- SALVAR EDIÇÃO ---
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
      const data = Object.fromEntries(formData.entries());

      fetch(editUrl, {
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
            bootstrap.Modal.getInstance(
              document.getElementById("modalEditarCliente")
            ).hide();
            // Atualiza a tela com os dados novos que voltaram do servidor
            selecionarCliente(result.cliente);
          } else {
            alert("Erro ao editar: " + result.message);
          }
        });
    });
  }
});

// --- FUNÇÕES GLOBAIS ---

function selecionarCliente(cliente) {
  // 1. Salva na variável global para edição posterior
  clienteAtualObj = cliente;

  // 2. Atualiza Interface
  document.getElementById("area-busca").classList.add("d-none");
  document
    .getElementById("card-cliente-selecionado")
    .classList.remove("d-none");

  document.getElementById("card-nome").innerText = cliente.nome;
  document.getElementById("card-ac").innerText = cliente.responsavel;

  // Formata endereço
  let enderecoCompleto = cliente.endereco_completo; // Se vier da API de Create/Edit
  if (!enderecoCompleto) {
    // Se vier da API de Busca (que retorna campos separados)
    enderecoCompleto = `${cliente.logradouro}, ${cliente.numero} - ${cliente.cidade}/${cliente.estado}`;
  }
  document.getElementById("card-endereco").innerText = enderecoCompleto;
  document.getElementById("card-cep").innerText = cliente.cep;

  // 3. Preenche Input Oculto
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

// --- LÓGICA TIPO TRANSPORTE (CARGA) ---
const selectTransporte = document.getElementById("id_tipo_transporte"); // ID padrão do Django
const divCodigoCarga = document.getElementById("divCodigoCarga");

if (selectTransporte && divCodigoCarga) {
  // Função para verificar o estado atual
  function checkTransporte() {
    if (selectTransporte.value === "carga") {
      // Valor deve ser minúsculo conforme o models.py choices
      divCodigoCarga.style.display = "block";
    } else {
      divCodigoCarga.style.display = "none";
      // Limpa o campo se mudar de ideia, para não salvar lixo
      const inputCarga = divCodigoCarga.querySelector("input");
      if (inputCarga) inputCarga.value = "";
    }
  }

  // Ouve mudanças
  selectTransporte.addEventListener("change", checkTransporte);

  // Roda ao carregar (caso tenha voltado de um erro de validação)
  checkTransporte();
}
