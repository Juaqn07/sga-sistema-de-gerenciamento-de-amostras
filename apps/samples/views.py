from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Processo
from .forms import ProcessoForm, ClienteForm


@login_required
def process_list_view(request):
    # Filtra processos baseados na função do usuário
    if request.user.funcao == 'Vendedor':
        # Vendedor vê apenas os seus
        processos = Processo.objects.filter(
            criado_por=request.user).order_by('-data_criacao')
    else:
        # Gestor e Separador veem todos
        processos = Processo.objects.all().order_by('-data_criacao')

    context = {
        'processos': processos,
        'total_processos': processos.count()
    }
    return render(request, 'samples/processos-do-setor.html', context)


@login_required
def process_create_view(request):
    # Apenas Vendedores e Gestores podem criar processos
    if request.user.funcao == 'Separador':
        messages.error(request, 'Você não tem permissão para criar processos.')
        return redirect('samples:lista_processos')

    if request.method == 'POST':
        processo_form = ProcessoForm(request.POST)
        cliente_form = ClienteForm(request.POST)

        if processo_form.is_valid() and cliente_form.is_valid():
            # 1. Salva o Cliente
            cliente = cliente_form.save()

            # 2. Prepara o Processo (sem salvar ainda)
            processo = processo_form.save(commit=False)

            # 3. Preenche os dados automáticos
            processo.cliente = cliente
            processo.criado_por = request.user

            # 4. Salva o Processo (o código será gerado automaticamente pelo model)
            processo.save()

            messages.success(request, 'Processo criado com sucesso!')
            return redirect('samples:lista_processos')
    else:
        processo_form = ProcessoForm()
        cliente_form = ClienteForm()

    context = {
        'processo_form': processo_form,
        'cliente_form': cliente_form
    }
    return render(request, 'samples/criar-processo.html', context)


@login_required
def process_detail_view(request, pk):
    # Busca o processo real ou retorna erro 404
    processo = get_object_or_404(Processo, pk=pk)

    return render(request, 'samples/detalhes-processo.html', {'processo': processo})
