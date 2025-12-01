from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.samples.models import Processo, EventoTimeline, Comentario


@login_required
def dashboard_view(request):
    """
    Controlador principal do Dashboard.

    Lógica de Negócio:
    Renderiza visualizações diferentes baseadas na Função do usuário logado:
    1. Gestor: KPIs globais, Gráficos de status e evolução.
    2. Vendedor: Foco em "Meus Processos" e notificações de andamento.
    3. Separador: Foco em "Fila de Espera" e tarefas atribuídas.
    """
    user = request.user
    context = {}

    # ==========================================================================
    # PERFIL 1: GESTOR (Visão Macro)
    # ==========================================================================
    if user.funcao == 'Gestor':

        # --- A. CÁLCULO DE KPIs (Indicadores Chave de Desempenho) ---

        # 1. Volume Ativo: Tudo que está rodando na empresa hoje
        processos_ativos = Processo.objects.exclude(
            status__in=['entregue', 'cancelado'])
        context['kpi_ativos'] = processos_ativos.count()

        # 2. Gargalo: Processos parados aguardando triagem
        context['kpi_fila'] = Processo.objects.filter(
            status='nao_atribuido').count()

        # 3. Qualidade: Ocorrências/Problemas reportados pela equipe
        ocorrencias = Comentario.objects.filter(
            encaminhar_gestao=True).order_by('-data')
        context['kpi_ocorrencias'] = ocorrencias.count()
        context['lista_ocorrencias'] = ocorrencias[:10]  # Top 10 recentes

        # --- B. PREPARAÇÃO DE DADOS PARA GRÁFICOS (Chart.js) ---

        # Gráfico 1: Distribuição por Status (Rosca)
        # Agrupa por status e conta os IDs. Ex: [{'status': 'pendente', 'total': 5}, ...]
        stats = Processo.objects.values('status').annotate(
            total=Count('id')).order_by()

        # Dicionário auxiliar para traduzir códigos ('em_separacao') para labels ('Em Separação')
        status_dict = dict(Processo.STATUS_CHOICES)

        labels = []
        data = []
        colors = []

        # Paleta de cores semântica (bootstrap-like)
        color_map = {
            'nao_atribuido': '#6c757d',  # Cinza
            'atribuido': '#495057',     # Cinza Escuro
            'em_separacao': '#0d6efd',  # Azul
            'pendente': '#ffc107',      # Amarelo (Atenção)
            'pronto_envio': '#0dcaf0',  # Ciano
            'em_rota': '#6610f2',       # Roxo
            'entregue': '#198754',      # Verde (Sucesso)
            'nao_entregue': '#dc3545',  # Vermelho (Erro)
            'cancelado': '#212529',     # Preto
        }

        for item in stats:
            s_code = item['status']
            # Popula as listas que serão convertidas em JSON no template
            labels.append(status_dict.get(s_code, s_code))
            data.append(item['total'])
            colors.append(color_map.get(s_code, '#adb5bd'))

        context['gestor_status_labels'] = labels
        context['gestor_status_data'] = data
        context['gestor_status_colors'] = colors

        # Gráfico 2: Evolução Semanal (Barras)
        # Calcula a entrada de processos nos últimos 7 dias
        hoje = timezone.now().date()
        dias = []
        qtds = []

        for i in range(7, 0, -1):
            data_alvo = hoje - timedelta(days=i)
            # Filtra pela data de criação (ignorando hora)
            qtd = Processo.objects.filter(data_criacao__date=data_alvo).count()

            dias.append(data_alvo.strftime('%d/%m'))
            qtds.append(qtd)

        context['gestor_weekly_labels'] = dias
        context['gestor_weekly_data'] = qtds

    # ==========================================================================
    # PERFIL 2: VENDEDOR (Visão de Acompanhamento)
    # ==========================================================================
    elif user.funcao == 'Vendedor':
        # Filtro Base: Apenas o que EU criei
        meus_processos = Processo.objects.filter(criado_por=user)

        # KPI: Meus Ativos (Em andamento)
        context['meus_ativos'] = meus_processos.exclude(
            status__in=['entregue', 'cancelado']
        ).count()

        # KPI: Meus Finalizados (Histórico de sucesso)
        context['meus_finalizados'] = meus_processos.filter(
            status='entregue'
        ).count()

        # FEED DE NOTIFICAÇÕES
        # Mostra atualizações (rastreio, status) feitas por OUTRAS pessoas/sistemas
        context['ultimas_atualizacoes'] = EventoTimeline.objects.filter(
            processo__in=meus_processos
        ).exclude(
            autor=user  # Não mostra o que eu mesmo fiz
        ).order_by('-data')[:6]

    # ==========================================================================
    # PERFIL 3: SEPARADOR (Visão Operacional)
    # ==========================================================================
    elif user.funcao == 'Separador':

        # KPI: Fila de Espera
        # Processos "livres" que precisam ser assumidos
        context['fila_espera'] = Processo.objects.filter(
            status='nao_atribuido',
            responsavel_separacao__isnull=True
        ).count()

        # KPI: Trabalho em Andamento (WIP)
        # Processos que já assumi e estou trabalhando
        context['meus_pendentes'] = Processo.objects.filter(
            responsavel_separacao=user
        ).exclude(
            status__in=['entregue', 'cancelado']
        ).count()

        # FEED DE ATIVIDADE RECENTE
        # Histórico das ações nos processos que cuido
        meus_atribuidos = Processo.objects.filter(responsavel_separacao=user)
        context['ultimas_atividades'] = EventoTimeline.objects.filter(
            processo__in=meus_atribuidos
        ).order_by('-data')[:6]

    return render(request, 'dashboard/dashboard.html', context)
