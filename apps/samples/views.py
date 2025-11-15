from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# View para a página de lista (processos-do-setor.html)


@login_required
def process_list_view(request):

    # (MAIS TARDE, buscaremos os processos do banco)
    # Por enquanto, enviamos uma lista vazia para testar o "molde"
    context = {
        'processos': [],  # Lista de processos (vazia por enquanto)
        'total_processos': 0
    }
    return render(request, 'samples/processos-do-setor.html', context)

# View para a página de criação (criar-processo.html)


@login_required
def process_create_view(request):
    # (A lógica do formulário virá aqui depois)
    return render(request, 'samples/criar-processo.html')

# View para a página de detalhes (detalhes-processo.html)


@login_required
def process_detail_view(request, pk):
    # O 'pk' vem da URL (ex: /processos/1/)

    # (MAIS TARDE, buscaremos o processo com o id=pk)
    # Por enquanto, podemos "fingir" um objeto para o molde
    context = {
        'processo': {
            'codigo': f'PRC-FAKE-{pk}',
            'get_status_display': 'Em Progresso (Fake)',
            'get_prioridade_display': 'Alta (Fake)',
            'titulo': 'Processo de Teste Falso',
            'descricao': 'Esta é uma descrição vinda da view.',
            'criado_por': {'get_full_name': 'Usuário Falso'},
            'data_criacao': None,  # (Django vai mostrar nada)
            'setor_atual': 'Separação (Fake)',
            'timeline': [],  # Timeline vazia por enquanto
            'tipo_amostra': 'Pré-forma PET (Fake)',
        }
    }
    return render(request, 'samples/detalhes-processo.html', context)
