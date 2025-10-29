<!DOCTYPE html>
<html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SGA - Processos do Setor</title>

    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
      rel="stylesheet"
    />

    <link rel="stylesheet" href="../css/layout.css" />

    <link rel="stylesheet" href="../css/processos-do-setor.css" />

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </head>
  <body>
    <header>
      <img src="../img/logo.png" alt="Logo - SGA" />
      <div class="menuHeader">
        <div class="dropdown">
          <a
            class="btn-outline-light btn btn-secondary dropdown-toggle"
            href="#"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            Gestor
          </a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="./perfil.php">Perfil</a></li>
            <li><a class="dropdown-item" href="./index.php">Sair</a></li>
          </ul>
        </div>
      </div>
    </header>

    <section>
      <div class="d-flex flex-column menuLateral text-light p-3">
        <a
          href="./dashboard.php"
          class="d-flex align-items-center mb-3 text-decoration-none text-light p-2 rounded hover-bg-light"
        >
          <i class="bi bi-house me-2"></i> Dashboard
        </a>
        <a
          href="./criar-processo.php"
          class="d-flex align-items-center mb-3 text-decoration-none text-light p-2 rounded hover-bg-light"
        >
          <i class="bi bi-file-earmark-plus me-2"></i> Criar Processo
        </a>
        <a
          href="./processos-do-setor.php"
          class="d-flex align-items-center mb-3 text-decoration-none text-light p-2 rounded hover-bg-light active-menu"
        >
          <i class="bi bi-folder2-open me-2"></i> Processos Do Setor
        </a>
        <a
          href="./cadastrar-usuario.php"
          class="d-flex align-items-center mb-3 text-decoration-none text-light p-2 rounded hover-bg-light"
        >
          <i class="bi bi-person-plus me-2"></i> Cadastrar Usuário
        </a>
      </div>
    </section>

    <div class="justify-content-between align-items-center titulo-descricao">
      <h4 class="mb-0 fw-semibold">Processos do Setor</h4>
      <small class="text-muted">2 de 2 processos</small>
    </div>

    <div class="container-fluid p-4">
      <div class="bg-white p-4 rounded shadow-sm">
        <div class="row g-3 align-items-center mb-4">
          <div class="col-md-6 col-lg-6">
            <input
              class="form-control"
              type="search"
              placeholder="Buscar por título, número, código de rastreio..."
              aria-label="Search"
            />
          </div>
          <div class="col-md-3 col-lg-3">
            <select class="form-select">
              <option selected>Todos os Status</option>
              <option>Não Atribuído</option>
              <option>Atribuído</option>
              <option>Em Separação</option>
              <option>Pendente</option>
              <option>Pronto para Envio</option>
              <option>Em Rota de Entrega</option>
              <option>Não Entregue</option>
              <option>Entregue</option>
            </select>
          </div>
          <div class="col-md-3 col-lg-3">
            <select class="form-select">
              <option selected>Todas as Prioridades</option>
              <option>Alta</option>
              <option>Normal</option>
              <option>Baixa</option>
            </select>
          </div>
        </div>

        <table class="table align-middle">
          <thead class="table-light">
            <tr>
              <th>Código/Rastreio</th>
              <th>Título</th>
              <th>Cliente</th>
              <th>Status</th>
              <th class="text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div class="fw-semibold">
                  PRC-2025-00123
                  <span class="badge bg-danger ms-1">Alta</span>
                </div>
                <div class="text-muted small">AA123456789BR</div>
              </td>
              <td>
                <div class="fw-semibold">Análise de Pré-forma - Lote A123</div>
                <div class="text-muted small">Pré-forma PET</div>
              </td>
              <td>
                <div class="fw-semibold">Empresa ABC Ltda</div>
                <div class="text-muted small">A/C: João Pereira</div>
              </td>
              <td>
                <span class="badge bg-primary-subtle text-primary px-3 py-2"
                  >Em Progresso</span
                >
              </td>

              <td class="text-center">
                <a
                  href="./detalhes-processo.php"
                  class="text-secondary"
                  title="Visualizar Detalhes"
                >
                  <i class="bi bi-eye me-2" role="button"></i>
                </a>
                <i
                  class="bi bi-pencil-square me-2 text-secondary"
                  role="button"
                  title="Alterar Status"
                  data-bs-toggle="modal"
                  data-bs-target="#modalAlterarStatus"
                  data-processo-id="PRC-2025-00123"
                  data-processo-titulo="Análise de Pré-forma - Lote A123"
                  data-processo-status="em-separacao"
                ></i>
                <i
                  class="bi bi-box me-2 text-secondary"
                  role="button"
                  title="Código de Rastreio"
                  data-bs-toggle="modal"
                  data-bs-target="#modalCodigoRastreio"
                  data-processo-id="PRC-2025-00123"
                  data-processo-titulo="Análise de Pré-forma - Lote A123"
                  data-processo-rastreio="AA123456789BR"
                ></i>
                <i
                  class="bi bi-chat-square-text me-2 text-secondary"
                  role="button"
                  title="Adicionar Comentário"
                  data-bs-toggle="modal"
                  data-bs-target="#modalAddComentario"
                  data-processo-id="PRC-2025-00123"
                  data-processo-titulo="Análise de Pré-forma - Lote A123"
                ></i>
                <i
                  class="bi bi-send text-secondary"
                  role="button"
                  title="Encaminhar"
                  data-bs-toggle="modal"
                  data-bs-target="#modalEncaminharProcesso"
                  data-processo-id="PRC-2025-00123"
                  data-processo-titulo="Análise de Pré-forma - Lote A123"
                ></i>
              </td>
            </tr>

            <tr>
              <td>
                <div class="fw-semibold">
                  PRC-2025-00124
                  <span class="badge bg-info-subtle text-info ms-1"
                    >Normal</span
                  >
                </div>
                <div class="text-muted small">CG-5467-2025</div>
              </td>
              <td>
                <div class="fw-semibold">
                  Teste de Garrafa Finalizada - Linha 02
                </div>
                <div class="text-muted small">Garrafa Finalizada</div>
              </td>
              <td>
                <div class="fw-semibold">Indústria XYZ S.A.</div>
                <div class="text-muted small">A/C: Maria Silva</div>
              </td>
              <td>
                <span class="badge bg-warning-subtle text-warning px-3 py-2"
                  >Pendente</span
                >
              </td>

              <td class="text-center">
                <a
                  href="./detalhes-processo.php"
                  class="text-secondary"
                  title="Visualizar Detalhes"
                >
                  <i class="bi bi-eye me-2" role="button"></i>
                </a>
                <i
                  class="bi bi-pencil-square me-2 text-secondary"
                  role="button"
                  title="Alterar Status"
                  data-bs-toggle="modal"
                  data-bs-target="#modalAlterarStatus"
                  data-processo-id="PRC-2025-00124"
                  data-processo-titulo="Teste de Garrafa Finalizada - Linha 02"
                  data-processo-status="pendente"
                ></i>
                <i
                  class="bi bi-box me-2 text-secondary"
                  role="button"
                  title="Código de Rastreio"
                  data-bs-toggle="modal"
                  data-bs-target="#modalCodigoRastreio"
                  data-processo-id="PRC-2025-00124"
                  data-processo-titulo="Teste de Garrafa Finalizada - Linha 02"
                  data-processo-rastreio="CG-5467-2025"
                ></i>
                <i
                  class="bi bi-chat-square-text me-2 text-secondary"
                  role="button"
                  title="Adicionar Comentário"
                  data-bs-toggle="modal"
                  data-bs-target="#modalAddComentario"
                  data-processo-id="PRC-2025-00124"
                  data-processo-titulo="Teste de Garrafa Finalizada - Linha 02"
                ></i>
                <i
                  class="bi bi-send text-secondary"
                  role="button"
                  title="Encaminhar"
                  data-bs-toggle="modal"
                  data-bs-target="#modalEncaminharProcesso"
                  data-processo-id="PRC-2025-00124"
                  data-processo-titulo="Teste de Garrafa Finalizada - Linha 02"
                ></i>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div
      class="modal fade"
      id="modalAlterarStatus"
      tabindex="-1"
      aria-labelledby="modalAlterarStatusLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="modalAlterarStatusLabel">
              Alterar Status
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p id="modalProcessoInfo" class="text-muted small"></p>
            <div class="mb-3">
              <label for="modalSelectStatus" class="form-label"
                >Novo Status</label
              >
              <select class="form-select" id="modalSelectStatus">
                <option value="nao-atribuido">Não Atribuído</option>
                <option value="atribuido">Atribuído</option>
                <option value="em-separacao">Em Separação</option>
                <option value="pendente">Pendente</option>
                <option value="pronto-envio">Pronto para Envio</option>
                <option value="em-rota">Em Rota de Entrega</option>
                <option value="nao-entregue">Não Entregue</option>
                <option value="entregue">Entregue</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              data-bs-dismiss="modal"
            >
              Cancelar
            </button>
            <button type="button" class="btn btn-success">
              <i class="bi bi-check-circle me-1"></i> Alterar Status
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      class="modal fade"
      id="modalCodigoRastreio"
      tabindex="-1"
      aria-labelledby="modalCodigoRastreioLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="modalCodigoRastreioLabel">
              Código de Rastreio
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p id="modalRastreioInfo" class="text-muted small"></p>
            <div class="mb-3">
              <label for="modalRastreioInput" class="form-label"
                >Código de Rastreio (13 dígitos)</label
              >
              <input
                type="text"
                class="form-control"
                id="modalRastreioInput"
                maxlength="13"
              />
              <small class="text-muted">13/13 caracteres</small>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              data-bs-dismiss="modal"
            >
              Cancelar
            </button>
            <button type="button" class="btn btn-success">
              <i class="bi bi-box-arrow-in-down me-1"></i> Salvar Código
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      class="modal fade"
      id="modalAddComentario"
      tabindex="-1"
      aria-labelledby="modalAddComentarioLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="modalAddComentarioLabel">
              Adicionar Comentário
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p id="modalComentarioInfo" class="text-muted small"></p>
            <div class="mb-3">
              <label for="modalComentarioTextarea" class="form-label"
                >Comentário</label
              >
              <textarea
                class="form-control"
                id="modalComentarioTextarea"
                rows="4"
                placeholder="Digite seu comentário sobre o processo..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              data-bs-dismiss="modal"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="btn btn-success"
              style="background-color: #5cb85c; border-color: #4cae4c"
            >
              <i class="bi bi-chat-square-text me-1"></i> Enviar Comentário
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      class="modal fade modal-encaminhar"
      id="modalEncaminharProcesso"
      tabindex="-1"
      aria-labelledby="modalEncaminharProcessoLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="modalEncaminharProcessoLabel">
              Encaminhar Processo
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p id="modalEncaminharInfo" class="text-muted small"></p>

            <div class="form-check mb-2">
              <input
                class="form-check-input"
                type="radio"
                name="encaminharOpcao"
                id="fluxoPadrao"
                value="padrao"
                checked
              />
              <label class="form-check-label p-3 rounded" for="fluxoPadrao">
                <strong class="d-block text-primary"
                  ><i class="bi bi-arrow-right-short"></i> Fluxo padrão do
                  sistema</strong
                >
                <small class="text-muted"
                  >O processo será encaminhado automaticamente para a próxima
                  etapa do fluxo.</small
                >
              </label>
            </div>

            <div class="form-check">
              <input
                class="form-check-input"
                type="radio"
                name="encaminharOpcao"
                id="fluxoGestao"
                value="gestao"
              />
              <label class="form-check-label p-3 rounded" for="fluxoGestao">
                <strong class="d-block"
                  ><i class="bi bi-exclamation-triangle"></i> Encaminhar para
                  Gestão</strong
                >
                <small class="text-muted"
                  >Envia o processo para análise de ocorrências pela
                  gestão.</small
                >
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              data-bs-dismiss="modal"
            >
              Cancelar
            </button>
            <button type="button" class="btn btn-success">
              <i class="bi bi-check-circle me-1"></i> Confirmar Encaminhamento
            </button>
          </div>
        </div>
      </div>
    </div>

    <script src="../js/processos-do-setor.js" defer></script>
  </body>
</html>
