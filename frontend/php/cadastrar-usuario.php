<!DOCTYPE html>
<html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cadastrar Usuário</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    />
    <link rel="stylesheet" href="../css/layout.css" />
    <link rel="stylesheet" href="../css/cadastrar-usuario.css" />
  </head>
  <body>
    <!-- Header -->
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

    <!-- Menu lateral -->
    <section>
      <div
        class="d-flex flex-column menuLateral text-light p-3"
        style="width: 250px; min-width: 180px; height: 100vh"
      >
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
          class="d-flex align-items-center mb-3 text-decoration-none text-light p-2 rounded hover-bg-light"
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
      <h4 class="mb-0">Cadastrar Novo Usuário</h4>
      <small>Adicione novos usuários ao sistema de gerenciamento de amostras</small>
    </div>

    <!-- Wrapper para os dois cards -->
    <div class="cards-wrapper">
      <!-- formulario de cadastro -->
      <div class="formulario-cadastro">
        <form>
          <div class="mb-4 p-4">
            <h3 class="d-flex align-items-center">
              <i class="bi bi-person-plus me-2"></i> Dados do Novo Usuário
            </h3>
            <p>Preencha as informações para criar uma nova conta de usuário</p>

            <div class="mb-3">
              <label for="nomeCompleto" class="form-label">Nome Completo</label>
              <input
                type="text"
                class="form-control"
                id="nomeCompleto"
                placeholder="nome completo do usuario"
              />
            </div>

            <div class="mb-3">
              <label for="exampleInputEmail1" class="form-label">Email</label>
              <input
                type="email"
                class="form-control"
                id="exampleInputEmail1"
                aria-describedby="emailHelp"
                placeholder="Email"
              />
              <div id="emailHelp" class="form-text"></div>
            </div>

            <div class="mb-3">
              <label for="exampleInputPassword1" class="form-label">Senha</label>
              <input
                type="password"
                class="form-control"
                id="exampleInputPassword1"
                placeholder="Senha Do Usuario "
              />
            </div>

            <div class="mb-3">
              <label for="funcaoSelect" class="form-label">Funçao</label>
              <select id="funcaoSelect" class="form-select">
                <option value="">Selecione a função</option>
                <option value="vendedor">Vendedor</option>
                <option value="separador">Separador</option>
                <option value="gestor">Gestor</option>
              </select>
            </div>

            <div class="mb-3">
              <label for="setorInput" class="form-label">setor</label>
              <input
                type="text"
                id="setorInput"
                class="form-control"
                placeholder="Setor Do Usuario"
              />
            </div>

            <button type="submit" class="btn btn-primary">
              Cadastrar Usuario
            </button>
          </div>
        </form>
      </div>

      <!-- card de usuários cadastrados -->
      <div class="usuarios-cadastrados-card">
        <div class="mb-4 p-4">
          <h3 class="d-flex align-items-center">
            <i class="bi bi-people me-2"></i> Usuários Cadastrados
          </h3>
          <p>Lista dos usuários ativos no sistema</p>

          <div class="lista-usuarios">
            <div class="usuario mb-3 p-3 border rounded d-flex flex-column gap-1">
              <label class="form-check-label">
                <input type="checkbox" class="form-check-input me-2" /> João Silva
              </label>
              <small>Email: joao@empresa.com</small>
              <small>Setor: Vendas</small>
              <small>Função: Vendedor</small>
            </div>

            <div class="usuario mb-3 p-3 border rounded d-flex flex-column gap-1">
              <label class="form-check-label">
                <input type="checkbox" class="form-check-input me-2" /> Maria
                Santos
              </label>
              <small>Email: maria@empresa.com</small>
              <small>Setor: Laboratório</small>
              <small>Função: Separador</small>
            </div>

            <div class="usuario mb-3 p-3 border rounded d-flex flex-column gap-1">
              <label class="form-check-label">
                <input type="checkbox" class="form-check-input me-2" /> Carlos
                Oliveira
              </label>
              <small>Email: carlos@empresa.com</small>
              <small>Setor: Qualidade</small>
              <small>Função: Separador</small>
            </div>
          </div>

          <button type="button" class="btn btn-danger mt-3">Excluir Usuário</button>
        </div>
      </div>
    </div>
  </body>
</html>
