<div align="center">
  <img src="./apps/core/static/core/img/logo.png" alt="Logo SGA" width="120">
  <h1>SGA - Sistema de Gerenciamento de Amostras</h1>
  
  <p>
    <b>Otimização, Rastreabilidade e Controle para Processos Industriais</b>
  </p>

  <p>
    <img src="https://img.shields.io/badge/status-em_desenvolvimento-yellow" alt="Status">
    <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python Version">
    <img src="https://img.shields.io/badge/django-5.0+-green" alt="Django Version">
    <img src="https://img.shields.io/badge/license-Proprietária-red" alt="License">
  </p>
</div>

---

## 📖 Sobre o Projeto

O **SGA** é uma solução web robusta desenvolvida para modernizar o fluxo de separação e análise de amostras industriais. O sistema substitui controles manuais e planilhas por um fluxo de trabalho digital, auditável e seguro.

Focado na experiência do usuário e na integridade dos dados, o SGA implementa conceitos de **"Pull System"** (auto-atribuição de tarefas), **Auditoria em Tempo Real** (Timeline) e **Hierarquia de Permissões**.

> Projeto desenvolvido como parte do Projeto Integrador do Curso Técnico em Informática do IFES.

---

## 🖥️ Visão Geral do Sistema

### 📊 Dashboards Personalizados

Visão centralizada dos indicadores de desempenho, com contadores de status e gráficos de produtividade semanal.

![Dashboard](screenshots/dashboard_gestor.png)
_(Visão do Gestor com indicadores e gráficos)_

---

## ✨ Principais Funcionalidades

### 1. Gestão de Processos (Core)

O coração do sistema, focado em agilidade e rastreabilidade.

- **Criação Inteligente:** Formulário de criação com busca de clientes via **AJAX** e cadastro rápido via Modal. Suporte a múltiplos tipos de amostra.
- **Listagem Avançada:** Filtros dinâmicos, paginação inteligente e separação visual ("Meus Processos" vs "Todos").
- **Fluxo de Atribuição:** Implementação de **Auto-atribuição**. Separadores visualizam a fila "Não Atribuída" e puxam a responsabilidade.

![Criação de Processo](screenshots/fluxo_criacao.png)

### 2. Rastreabilidade e Timeline

Cada processo possui uma **Timeline** imutável que registra automaticamente:

- Criação, Atribuição e Mudanças de Status.
- Alterações críticas em dados do Cliente (Auditoria).
- Uploads de anexos e registro de ocorrências.

Durante a fase de desenvolvimento, o rastreamento via correios é funcional de forma manual (ao clicar no botão de atualizar), mas a automação via Celery já está preparada para futuras integrações.

![Detalhes e Timeline](screenshots/detalhes_timeline.png)

### 3. Módulo Administrativo (`accounts`)

- **Controle de Acesso (RBAC):** Três níveis de permissão (Gestor, Vendedor, Separador).
- **Segurança:** Implementação de **Soft Delete** (Inativação) de usuários.

### 4. Integração Logística (Correios) 📦 _(Novo)_

Integração direta com a API CWS dos Correios para monitoramento de entregas.

- **Sincronização de Eventos:** Botão para atualizar o rastreio diretamente na tela de detalhes.
- **Automação de Status:** O sistema detecta eventos como "Objeto Entregue" ou "Devolvido" e atualiza o status do processo automaticamente.
- **Validação de Endereço:** Autocomplete de endereço via CEP na criação de clientes.

---

## ⚙️ Configuração e Ambiente (.env)

O sistema utiliza a biblioteca `python-decouple` para gerenciar configurações sensíveis. Antes de rodar o projeto, você deve criar um arquivo `.env` na raiz do projeto (baseado no `.env.example`, se houver) com as seguintes chaves:

```ini
# Configurações do Django
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# 📦 Configurações da API dos Correios (CWS)
CORREIOS_USER=seu_usuario_meus_correios
CORREIOS_CODIGO_ACESSO=sua_senha_de_acesso_api
CORREIOS_CONTRATO=numero_do_contrato
CORREIOS_CARTAO=numero_do_cartao_postagem
CORREIOS_URL_BASE=[https://api.correios.com.br](https://api.correios.com.br)
```

### ⚠️ Requisitos da API dos Correios

Para que as funcionalidades de rastreamento funcionem corretamente, é necessário:

1.  **Cadastro no "Meus Correios":** A empresa deve possuir conta ativa no portal dos Correios.
2.  **Contrato Jurídico:** A API de Rastreamento (SRO) e a geração de Tokens (CWS) exigem um Contrato de Cartão de Postagem ativo.
3.  **Credenciais:** As chaves de acesso devem ser geradas no portal do desenvolvedor dos Correios.

> 🔗 **Documentação Oficial:** [Correios CWS - Manual Técnico](https://www.correios.com.br/atendimento/developers/manuais/correioswebservice)

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Django 5 (MVT Architecture)
- **Frontend:** HTML5, CSS3 (Custom + Bootstrap 5), JavaScript (Vanilla + Fetch API)
- **Banco de Dados:** SQLite3 (Dev) / MySQL (Prod - _Planejado_)
- **Integrações:** API REST Correios (CWS/SRO).
- **Bibliotecas Chave:**
  - `python-decouple`: Gestão de variáveis de ambiente.
  - `requests`: Consumo de APIs externas.
  - `Pillow`: Processamento de imagens.
  - `Chart.js`: Gráficos dinâmicos.

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.10+
- Git

### Passo a Passo

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/Juaqn07/sga-sistema-de-gerenciamento-de-amostras.git](https://github.com/Juaqn07/sga-sistema-de-gerenciamento-de-amostras.git)
    cd sga-sistema-de-gerenciamento-de-amostras/sga
    ```

2.  **Crie e ative o ambiente virtual:**

    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\activate
    # Linux/Mac: source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o `.env`:**
    Crie o arquivo `.env` na raiz conforme explicado na seção "Configuração".

5.  **Execute as migrações e crie o Superusuário:**

    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

    > _Siga as instruções no terminal para definir usuário, e-mail e senha do administrador._

6.  **Execute o servidor:**

    ```bash
    python manage.py runserver
    ```

---

## ⚡ Configuração Inicial (Primeiros Passos)

Após rodar o servidor pela primeira vez, é necessário popular o banco de dados com informações básicas para o sistema operar corretamente.

### 1\. Acessar o Painel Administrativo

Acesse `http://127.0.0.1:8000/admin` e faça login com o **Superusuário** criado na instalação.

### 2\. Cadastrar Tipos de Amostra (Obrigatório)

Para criar um novo processo, o sistema exige tipos de amostra pré-definidos.

1.  No Admin, vá em **Samples \> Tipos de Amostra**.
2.  Adicione itens como:
    - `Frasco PET`
    - `Tampa Plástica`
    - `Rótulo`
    - `Pré-forma`
    - `Outros`

### 3\. Criar Usuários Operacionais

Para testar os diferentes perfis de acesso, crie usuários com as seguintes funções no Admin ou na tela de "Gerenciar Usuários" (se logado como Gestor):

- **Vendedor:** Para criar e acompanhar pedidos.
- **Separador:** Para visualizar a fila de separação e atribuir tarefas.
- **Gestor:** Para visualizar KPIs e relatórios.

---

## 👥 Equipe

| Nome                         | Função                   |
| :--------------------------- | :----------------------- |
| **Diego de Souza Gonoring**  | Front-End / Prototipagem |
| **Julia Soares Moreira**     | Front-End / Prototipagem |
| **Juan Ferreira dos Santos** | Back-End / Arquitetura   |
| **Evelin Santos de Jesus**   | Documentação             |

---

## ⚖️ Licença

Este é um software proprietário desenvolvido para fins acadêmicos e comerciais.
Todos os direitos reservados © 2025 - Equipe SGA.
