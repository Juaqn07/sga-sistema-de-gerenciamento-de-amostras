from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# View para a página de dashboard


@login_required
def dashboard_view(request):

    # (MAIS TARDE, vamos adicionar a lógica de contagem aqui)
    #
    labels_do_grafico = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"]
    dados_do_grafico = [0, 23, 15, 22, 20, 17]
    context = {
        # PLACEHOLDERS
        'contagem_processos_setor': 0,
        'contagem_processos_pendentes': 0,
        'contagem_processos_atrasados': 0,
        'chart_labels': labels_do_grafico,
        'chart_data': dados_do_grafico,

    }

    return render(request, 'dashboard/dashboard.html', context)
