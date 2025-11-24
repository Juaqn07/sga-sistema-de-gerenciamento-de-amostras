from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Processo, Cliente, Anexo, EventoTimeline
from .forms import ProcessoForm, ClienteForm
# Para busca de clientes no formulário (AJAX)
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
# Para o CRUD de clientes
from django.core.paginator import Paginator


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
    if request.user.funcao == 'Separador':
        messages.error(request, 'Você não tem permissão para criar processos.')
        return redirect('samples:lista_processos')

    if request.method == 'POST':
        processo_form = ProcessoForm(request.POST, request.FILES)

        # Pega o ID do input oculto
        cliente_id = request.POST.get('selected_cliente_id')

        # Validações
        if not cliente_id:
            messages.error(
                request, 'Por favor, selecione ou cadastre um destinatário.')
        elif processo_form.is_valid():
            try:
                cliente = Cliente.objects.get(id=cliente_id)

                processo = processo_form.save(commit=False)
                processo.cliente = cliente  # Vincula o cliente selecionado
                processo.criado_por = request.user
                processo.status = 'nao_atribuido'
                processo.save()
                processo_form.save_m2m()

                arquivo_enviado = processo_form.cleaned_data.get(
                    'arquivo_pedido')
                if arquivo_enviado:
                    Anexo.objects.create(
                        processo=processo,
                        arquivo=arquivo_enviado
                    )

                EventoTimeline.objects.create(
                    processo=processo,
                    titulo="Processo Criado",
                    descricao=f"Processo iniciado por {request.user.get_full_name() or request.user.username}.",
                    autor=request.user,
                    icone="bi-plus-circle-fill"  # Ícone de 'novo'
                )
                messages.success(request, 'Processo criado com sucesso!')
                return redirect('samples:lista_processos')

            except Cliente.DoesNotExist:
                messages.error(
                    request, 'Erro: Cliente selecionado não encontrado.')
    else:
        processo_form = ProcessoForm()

    context = {
        'processo_form': processo_form,
    }
    return render(request, 'samples/criar-processo.html', context)


@login_required
def process_detail_view(request, pk):
    # Busca o processo real ou retorna erro 404
    processo = get_object_or_404(Processo, pk=pk)

    return render(request, 'samples/detalhes-processo.html', {'processo': processo})


@login_required
def search_clientes_api(request):
    term = request.GET.get('term', '')
    # Pesquisa por nome, cnpj/cpf (se tiver) ou email
    clientes = Cliente.objects.filter(
        models.Q(nome__icontains=term) |
        models.Q(responsavel__icontains=term)
    )[:10]  # Limita a 10 resultados

    results = []
    for c in clientes:
        results.append({
            'id': c.id,
            'nome': c.nome,
            'responsavel': c.responsavel,
            'cidade': c.cidade,
            'estado': c.estado,
            'logradouro': c.logradouro,
            'numero': c.numero,
            'cep': c.cep
        })

    return JsonResponse({'results': results})


@login_required
@require_http_methods(["POST"])
def create_cliente_api(request):
    try:
        data = json.loads(request.body)
        # Cria o cliente direto
        cliente = Cliente.objects.create(
            nome=data.get('nome'),
            responsavel=data.get('responsavel'),
            cep=data.get('cep'),
            logradouro=data.get('logradouro'),
            numero=data.get('numero'),
            complemento=data.get('complemento'),
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
        )
        return JsonResponse({
            'status': 'success',
            'cliente': {
                'id': cliente.id,
                'nome': cliente.nome,
                'responsavel': cliente.responsavel,
                'endereco': f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}",
                'cep': cliente.cep
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def edit_cliente_api(request, pk):
    try:
        cliente = get_object_or_404(Cliente, pk=pk)
        data = json.loads(request.body)

        # Atualiza os campos
        cliente.nome = data.get('nome')
        cliente.responsavel = data.get('responsavel')
        cliente.cep = data.get('cep')
        cliente.logradouro = data.get('logradouro')
        cliente.numero = data.get('numero')
        cliente.complemento = data.get('complemento')
        cliente.bairro = data.get('bairro')
        cliente.cidade = data.get('cidade')
        cliente.estado = data.get('estado')

        cliente.save()

        return JsonResponse({
            'status': 'success',
            'cliente': {
                'id': cliente.id,
                'nome': cliente.nome,
                'responsavel': cliente.responsavel,
                'cep': cliente.cep,
                'logradouro': cliente.logradouro,
                'numero': cliente.numero,
                'complemento': cliente.complemento,
                'bairro': cliente.bairro,
                'cidade': cliente.cidade,
                'estado': cliente.estado,
                'endereco_completo': f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}"
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# -- CRUD Clientes --

@login_required
def cliente_list_view(request):
    # Busca
    query = request.GET.get('q')
    clientes_list = Cliente.objects.all().order_by('nome')

    if query:
        clientes_list = clientes_list.filter(
            models.Q(nome__icontains=query) |
            models.Q(responsavel__icontains=query) |
            models.Q(cidade__icontains=query)
        )

    # Paginação (10 por página)
    paginator = Paginator(clientes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'samples/lista-clientes.html', context)


@login_required
def cliente_create_view(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('samples:lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'samples/form-cliente.html', {'form': form})


@login_required
def cliente_update_view(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('samples:lista_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'samples/form-cliente.html', {'form': form})


@login_required
def cliente_delete_view(request, pk):
    # Apenas Gestores podem deletar clientes (Regra de negócio opcional)
    if request.user.funcao != 'Gestor':
        messages.error(request, 'Apenas gestores podem excluir clientes.')
        return redirect('samples:lista_clientes')

    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=pk)
        try:
            cliente.delete()
            messages.success(request, 'Cliente excluído com sucesso.')
        except models.ProtectedError:
            messages.error(
                request, 'Não é possível excluir este cliente pois ele possui Processos vinculados.')

    return redirect('samples:lista_clientes')
