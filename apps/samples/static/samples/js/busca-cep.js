/**
 * Configura a funcionalidade de Autocomplete de CEP via API.
 * Gerencia validação visual, feedback de loading e bloqueio do botão de envio.
 * * @param {string} cepSelector - Seletor CSS do input de CEP (ex: '#id_cep').
 * @param {object} fieldsMap - Objeto mapeando campos da API para seletores do DOM.
 * Ex: { logradouro: '#id_end', bairro: '#id_bairro' ... }
 * @param {string} [submitBtnSelector=null] - (Opcional) Seletor do botão de submit
 * para bloquear durante a validação.
 */
function setupCepAutocomplete(
  cepSelector,
  fieldsMap,
  submitBtnSelector = null
) {
  const inputCep = document.querySelector(cepSelector);
  const submitBtn = submitBtnSelector
    ? document.querySelector(submitBtnSelector)
    : null;

  if (!inputCep) return;

  // Cria dinamicamente a div de feedback (status) abaixo do input, se não existir
  let statusDiv = inputCep.parentNode.querySelector(".cep-status");
  if (!statusDiv) {
    statusDiv = document.createElement("div");
    statusDiv.className = "cep-status form-text mt-1";
    inputCep.parentNode.appendChild(statusDiv);
  }

  // --- 1. EVENTO INPUT: Limpeza e Bloqueio ---
  // Acionado a cada tecla digitada
  inputCep.addEventListener("input", function () {
    inputCep.classList.remove("is-valid", "is-invalid");
    statusDiv.innerHTML = "";
    if (submitBtn) submitBtn.disabled = true; // Bloqueia preventivamente
  });

  // --- 2. EVENTO BLUR: Validação e Busca ---
  // Acionado quando o campo perde o foco
  inputCep.addEventListener("blur", function () {
    const cep = this.value.replace(/\D/g, "");

    // A. Campo Vazio (Ignora, validation HTML5 required cuidará disso)
    if (cep.length === 0) return;

    // B. CEP Incompleto
    if (cep.length !== 8) {
      setInvalidState("CEP incompleto (deve ter 8 dígitos).");
      return;
    }

    // C. Início da Consulta API
    setLoadingState();

    fetch(`/correios/api/consulta-cep/?cep=${cep}`)
      .then((r) => r.json())
      .then((data) => {
        resetLoadingState();

        if (data.status === "success") {
          setValidState();
          fillFields(data.data);
        } else {
          setInvalidState("CEP não encontrado.");
          clearFields();
        }
      })
      .catch((err) => {
        resetLoadingState();
        statusDiv.innerHTML =
          '<span class="text-danger">Erro de conexão.</span>';
        console.error("Erro busca CEP:", err);
      });
  });

  // --- HELPER FUNCTIONS (Funções Auxiliares Internas) ---

  function setLoadingState() {
    inputCep.style.cursor = "wait";
    inputCep.readOnly = true;
    statusDiv.innerHTML =
      '<span class="text-primary"><span class="spinner-border spinner-border-sm"></span> Validando CEP...</span>';
  }

  function resetLoadingState() {
    inputCep.style.cursor = "text";
    inputCep.readOnly = false;
  }

  function setValidState() {
    inputCep.classList.add("is-valid");
    statusDiv.innerHTML =
      '<span class="text-success"><i class="bi bi-check-circle"></i> CEP Válido</span>';
    if (submitBtn) submitBtn.disabled = false;
  }

  function setInvalidState(msg) {
    inputCep.classList.add("is-invalid");
    statusDiv.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle"></i> ${msg}</span>`;
    if (submitBtn) submitBtn.disabled = true;
  }

  function fillFields(data) {
    for (const [key, selector] of Object.entries(fieldsMap)) {
      const field = document.querySelector(selector);
      if (field) {
        field.value = data[key] || "";
        field.classList.remove("is-invalid");
      }
    }
    // Foca no campo número para agilizar a digitação
    if (fieldsMap.numero) document.querySelector(fieldsMap.numero)?.focus();
  }

  function clearFields() {
    for (const selector of Object.values(fieldsMap)) {
      const field = document.querySelector(selector);
      if (field) field.value = "";
    }
  }
}
