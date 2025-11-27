from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.samples.models import Processo, EventoTimeline, Comentario


@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    # ==========================================================================
    # LÓGICA DO GESTOR
    # ==========================================================================
    if user.funcao == 'Gestor':

        # 1. KPIs (Indicadores Chave)
        # Total de processos ativos (não cancelados/entregues)
        processos_ativos = Processo.objects.exclude(
            status__in=['entregue', 'cancelado'])
        context['kpi_ativos'] = processos_ativos.count()

        # Processos parados na fila (Gargalo)
        context['kpi_fila'] = Processo.objects.filter(
            status='nao_atribuido').count()

        # Ocorrências não resolvidas
        # Comentários marcados como "Encaminhar para Gestão"
        ocorrencias = Comentario.objects.filter(
            encaminhar_gestao=True).order_by('-data')
        context['kpi_ocorrencias'] = ocorrencias.count()
        # As 5 mais recentes para a tabela
        context['lista_ocorrencias'] = ocorrencias[:10]

        # 2. Gráfico de Status (Rosca)
        # Agrupa e conta para não fazer query dentro de loop
        # Ex: {'status': 'pendente', 'total': 5}
        stats = Processo.objects.values('status').annotate(
            total=Count('id')).order_by()

        # Traduz os códigos do banco ('em_separacao') para texto ('Em Separação')
        status_dict = dict(Processo.STATUS_CHOICES)

        labels = []
        data = []
        colors = []

        # Mapeamento de cores profissionais para o gráfico
        color_map = {
            'nao_atribuido': '#6c757d',
            'atribuido': '#495057',
            'em_separacao': '#0d6efd',
            'pendente': '#ffc107',
            'pronto_envio': '#0dcaf0',
            'em_rota': '#6610f2',
            'entregue': '#198754',
            'nao_entregue': '#dc3545',
            'cancelado': '#212529',
        }

        for item in stats:
            s_code = item['status']
            labels.append(status_dict.get(s_code, s_code))
            data.append(item['total'])
            colors.append(color_map.get(s_code, '#adb5bd'))

        context['gestor_status_labels'] = labels
        context['gestor_status_data'] = data
        context['gestor_status_colors'] = colors

        # 3. Gráfico de Evolução Semanal (Barras)
        # Pega os últimos 7 dias
        hoje = timezone.now().date()
        dias = []
        qtds = []

        for i in range(7, 0, -1):
            data_alvo = hoje - timedelta(days=i)
            qtd = Processo.objects.filter(data_criacao__date=data_alvo).count()
            dias.append(data_alvo.strftime('%d/%m'))
            qtds.append(qtd)

        context['gestor_weekly_labels'] = dias
        context['gestor_weekly_data'] = qtds

    # ==========================================================================
    # 2. VISÃO DO VENDEDOR
    # ==========================================================================
    elif user.funcao == 'Vendedor':
        # Meus Processos
        meus_processos = Processo.objects.filter(criado_por=user)

        # KPI: Ativos (Tudo que não acabou nem foi cancelado)
        context['meus_ativos'] = meus_processos.exclude(
            status__in=['entregue', 'cancelado']).count()

        # KPI: Finalizados (Sucesso)
        context['meus_finalizados'] = meus_processos.filter(
            status=['entregue']).count()

        # FEED DE NOTIFICAÇÕES
        # Mostra eventos nos meus processos que NÃO foram feitos por mim.
        context['ultimas_atualizacoes'] = EventoTimeline.objects.filter(
            processo__in=meus_processos
        ).exclude(
            autor=user  # Exclui minhas próprias ações para não poluir
        ).order_by('-data')[:6]  # Top 6 recentes

    # ==========================================================================
    # 3. VISÃO DO SEPARADOR
    # ==========================================================================
    elif user.funcao == 'Separador':
        # KPI: Fila de Espera (Sinal de Alerta)
        # Processos sem dono e marcados como não atribuídos
        context['fila_espera'] = Processo.objects.filter(
            status='nao_atribuido',
            responsavel_separacao__isnull=True
        ).count()

        # KPI: Meus Pendentes (Work in Progress)
        # Processos assumidos e ainda não encerrados
        context['meus_pendentes'] = Processo.objects.filter(
            responsavel_separacao=user
        ).exclude(
            status__in=['entregue', 'cancelado']
        ).count()

        # FEED DE ATIVIDADE
        meus_atribuidos = Processo.objects.filter(responsavel_separacao=user)
        context['ultimas_atividades'] = EventoTimeline.objects.filter(
            processo__in=meus_atribuidos
        ).order_by('-data')[:6]

    return render(request, 'dashboard/dashboard.html', context)
