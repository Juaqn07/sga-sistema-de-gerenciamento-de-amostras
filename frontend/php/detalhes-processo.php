<!DOCTYPE html>
<html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SGA - Detalhes do Processo</title>

    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
      rel="stylesheet"
    />

    <link rel="stylesheet" href="../css/layout.css" />

    <link rel="stylesheet" href="../css/detalhes-processo.css" />

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

    <main class="process-wrapper">
      <div
        class="page-header d-flex justify-content-between align-items-center"
      >
        <div>
          <a href="./processos-do-setor.php" class="btn-back mb-2 d-block">
            <i class="bi bi-arrow-left"></i> Voltar
          </a>
          <div class="d-flex align-items-center gap-3">
            <h2>PRC-2025-00123</h2>
            <span class="badge bg-primary-subtle text-primary"
              >Em Progresso</span
            >
            <span class="badge bg-danger-subtle text-danger">Alta</span>
          </div>
          <p class="text-muted fs-5 mb-0">Análise de Pré-forma - Lote A123</p>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-primary">
            <i class="bi bi-send"></i> Encaminhar
          </button>
          <button class="btn btn-outline-secondary">
            <i class="bi bi-three-dots"></i>
          </button>
        </div>
      </div>

      <div class="row g-4 mt-2">
        <div class="col-lg-8 process-layout-main">
          <div class="card mb-4">
            <div class="card-body p-4">
              <h5 class="card-title fw-semibold">Informações do Processo</h5>

              <h6 class="mt-4">Descrição</h6>
              <p>
                Análise completa de pré-formas para verificação de propriedades
                físicas e químicas conforme especificações.
              </p>

              <div class="info-card-footer d-flex justify-content-between">
                <div class="info-item">
                  <i class="bi bi-person"></i>
                  <span>Criado por <strong>João Silva</strong></span>
                </div>
                <div class="info-item">
                  <i class="bi bi-calendar-event"></i>
                  <span
                    >Data de criação <strong>15/01/2025, 05:30</strong></span
                  >
                </div>
                <div class="info-item">
                  <i class="bi bi-building"></i>
                  <span>Setor atual <strong>Separação</strong></span>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <ul
                class="nav nav-tabs card-header-tabs"
                id="processTabs"
                role="tablist"
              >
                <li class="nav-item" role="presentation">
                  <button
                    class="nav-link active"
                    id="timeline-tab"
                    data-bs-toggle="tab"
                    data-bs-target="#timeline"
                    type="button"
                    role="tab"
                    aria-controls="timeline"
                    aria-selected="true"
                  >
                    Timeline
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button
                    class="nav-link"
                    id="anexos-tab"
                    data-bs-toggle="tab"
                    data-bs-target="#anexos"
                    type="button"
                    role="tab"
                    aria-controls="anexos"
                    aria-selected="false"
                  >
                    Anexos (2)
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button
                    class="nav-link"
                    id="comentarios-tab"
                    data-bs-toggle="tab"
                    data-bs-target="#comentarios"
                    type="button"
                    role="tab"
                    aria-controls="comentarios"
                    aria-selected="false"
                  >
                    Comentários (1)
                  </button>
                </li>
              </ul>
            </div>

            <div class="card-body p-4 tab-content" id="processTabsContent">
              <div
                class="tab-pane fade show active"
                id="timeline"
                role="tabpanel"
                aria-labelledby="timeline-tab"
              >
                <h5 class="fw-semibold">Histórico do Processo</h5>
                <p class="text-muted">
                  Acompanhe todas as movimentações e atualizações
                </p>

                <ul class="process-timeline">
                  <li class="timeline-item">
                    <div class="timeline-icon">
                      <i class="bi bi-check-lg"></i>
                    </div>
                    <div class="timeline-content">
                      <strong>Processo criado</strong>
                      <small>Por João Silva • 15/01/2025, 05:30</small>
                    </div>
                  </li>
                  <li class="timeline-item">
                    <div class="timeline-icon"><i class="bi bi-send"></i></div>
                    <div class="timeline-content">
                      <strong>Encaminhado para separação</strong>
                      <small>Por Maria Santos • 15/01/2025, 06:15</small>
                    </div>
                    <div class="timeline-note">
                      Amostra recebida em perfeitas condições
                    </div>
                  </li>
                  <li class="timeline-item">
                    <div class="timeline-icon">
                      <i class="bi bi-box-seam"></i>
                    </div>
                    <div class="timeline-content">
                      <strong>Separação iniciada</strong>
                      <small>Por Carlos Oliveira • 16/01/2025, 11:20</small>
                    </div>
                  </li>
                </ul>
              </div>

              <div
                class="tab-pane fade"
                id="anexos"
                role="tabpanel"
                aria-labelledby="anexos-tab"
              >
                <p>Conteúdo dos Anexos aqui...</p>
              </div>

              <div
                class="tab-pane fade"
                id="comentarios"
                role="tabpanel"
                aria-labelledby="comentarios-tab"
              >
                <p>Conteúdo dos Comentários aqui...</p>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4 process-layout-sidebar">
          <div class="card mb-4 details-card">
            <div class="card-header">
              <h5 class="mb-0 fw-semibold">Detalhes</h5>
            </div>
            <div class="card-body p-4">
              <div class="detail-item">
                <label>Tipo de Amostra</label>
                <p>Pré-forma PET</p>
              </div>
              <div class="detail-item">
                <label>Prioridade</label>
                <p><span class="badge bg-danger">Alta</span></p>
              </div>

              <div class="detail-item">
                <div class="d-flex justify-content-between align-items-center">
                  <label>Status</label>
                  <a
                    href="#"
                    class="text-primary"
                    title="Alterar Status"
                    data-bs-toggle="modal"
                    data-bs-target="#modalAlterarStatus"
                  >
                    <i class="bi bi-pencil-square"></i>
                  </a>
                </div>
                <p><span class="badge bg-primary">Em Progresso</span></p>
              </div>

              <div class="detail-item mb-0">
                <label>Última Atualização</label>
                <p>16/01/2025, 11:20</p>
              </div>
            </div>
          </div>

          <div class="card mb-4 actions-card">
            <div class="card-header">
              <h5 class="mb-0 fw-semibold">Ações</h5>
            </div>
            <div class="card-body p-3">
              <div class="d-grid gap-2">
                <button class="btn btn-primary">
                  <i class="bi bi-send"></i> Encaminhar
                </button>
                <button class="btn btn-outline-secondary">
                  <i class="bi bi-plus-circle"></i> Solicitar Complemento
                </button>
                <button class="btn btn-outline-secondary">
                  <i class="bi bi-check-circle"></i> Marcar como Concluído
                </button>
                <button class="btn btn-outline-secondary">
                  <i class="bi bi-download"></i> Exportar Relatório
                </button>
              </div>
            </div>
          </div>

          <div class="card stats-card">
            <div class="card-header">
              <h5 class="mb-0 fw-semibold">Estatísticas</h5>
            </div>
            <div class="card-body p-4">
              <div
                class="stat-item d-flex justify-content-between align-items-center mb-2"
              >
                <span>Anexos</span>
                <span class="stat-value">2</span>
              </div>
              <div
                class="stat-item d-flex justify-content-between align-items-center mb-2"
              >
                <span>Comentários</span>
                <span class="stat-value">1</span>
              </div>
              <div
                class="stat-item d-flex justify-content-between align-items-center"
              >
                <span>Eventos</span>
                <span class="stat-value">3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

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
            <p class="text-muted small">
              PRC-2025-00123 - Análise de Pré-forma - Lote A123
            </p>

            <div class="mb-3">
              <label for="selectNovoStatus" class="form-label"
                >Novo Status</label
              >
              <select class="form-select" id="selectNovoStatus">
                <option value="nao-atribuido">Não Atribuído</option>
                <option value="atribuido">Atribuído</option>
                <option value="em-separacao" selected>Em Separação</option>
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
  </body>
</html>
