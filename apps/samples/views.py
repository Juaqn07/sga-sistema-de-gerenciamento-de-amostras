from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, ProtectedError, F, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json

from .models import Processo, Cliente, Anexo, EventoTimeline, Comentario
from .forms import ProcessoForm, ClienteForm, AnexoForm

# ==============================================================================
# BLOCO 1: VIEWS DE PROCESSOS (CRUD E VISUALIZAÇÃO)
# ==============================================================================


@login_required
def process_list_view(request):
    user = request.user

    # --- 1. QUERYSET BASE ---
    if user.funcao == 'Vendedor':
        base_qs = Processo.objects.filter(criado_por=user)
    elif user.funcao == 'Separador':
        base_qs = Processo.objects.filter(
            Q(responsavel_separacao=user) | Q(
                responsavel_separacao__isnull=True)
        )
    else:
        # Gestor vê tudo
        base_qs = Processo.objects.all()

    # --- 2. FILTROS ---
    q = request.GET.get('q')
    status_filter = request.GET.get('status')
    prioridade_filter = request.GET.get('prioridade')

    if q:
        base_qs = base_qs.filter(
            Q(codigo__icontains=q) |
            Q(titulo__icontains=q) |
            Q(codigo_rastreio__icontains=q) |
            Q(cliente__nome__icontains=q)
        )
    if status_filter:
        base_qs = base_qs.filter(status=status_filter)
    if prioridade_filter:
        base_qs = base_qs.filter(prioridade=prioridade_filter)

    # Ordenação padrão
    base_qs = base_qs.order_by('-data_criacao')

    # --- 3. SEPARAÇÃO PARA GESTOR ---
    meus_processos_page_obj = None  # Variável para a paginação dos meus processos

    if user.funcao == 'Gestor':
        # Separa "Meus Processos"
        meus_qs = base_qs.filter(
            Q(criado_por=user) | Q(responsavel_separacao=user)
        )

        # Remove "Meus Processos" da lista geral
        processos_qs = base_qs.exclude(id__in=meus_qs.values('id'))

        # PAGINAÇÃO 1: MEUS PROCESSOS (Usando 'mp_page')
        mp_paginator = Paginator(meus_qs, 5)
        mp_page_number = request.GET.get('mp_page')
        meus_processos_page_obj = mp_paginator.get_page(mp_page_number)

    else:
        processos_qs = base_qs

    # --- 4. PAGINAÇÃO 2: LISTA PRINCIPAL (Usando 'page') ---
    paginator = Paginator(processos_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'meus_processos': meus_processos_page_obj,  # Agora enviamos o objeto paginado
        'page_obj': page_obj,
        'total_processos': paginator.count + (meus_processos_page_obj.paginator.count if meus_processos_page_obj else 0),
        'status_choices': Processo.STATUS_CHOICES,
        'prioridade_choices': Processo.PRIORIDADE_CHOICES,
    }
    return render(request, 'samples/processos-do-setor.html', context)


@login_required
def process_create_view(request):
    """
    Gerencia a criação de processos, incluindo a criação simultânea de clientes
    e upload inicial de anexos.
    """
    if request.user.funcao == 'Separador':
        messages.error(request, 'Você não tem permissão para criar processos.')
        return redirect('samples:lista_processos')

    if request.method == 'POST':
        processo_form = ProcessoForm(request.POST, request.FILES)

        # O ID do cliente vem de um input oculto (preenchido via busca AJAX ou Modal)
        cliente_id = request.POST.get('selected_cliente_id')

        if not cliente_id:
            messages.error(
                request, 'Por favor, selecione ou cadastre um destinatário.')
        elif processo_form.is_valid():
            try:
                cliente = Cliente.objects.get(id=cliente_id)

                # Salva o processo mas não comita ainda para injetar dados
                processo = processo_form.save(commit=False)
                processo.cliente = cliente
                processo.criado_por = request.user
                processo.status = 'nao_atribuido'
                processo.save()

                # Salva relacionamento ManyToMany (Tipos de Amostra)
                processo_form.save_m2m()

                # Processa anexo inicial (Pedido Iniflex, etc)
                arquivo_enviado = processo_form.cleaned_data.get(
                    'arquivo_pedido')
                if arquivo_enviado:
                    Anexo.objects.create(
                        processo=processo,
                        arquivo=arquivo_enviado
                    )

                # Registro inicial na Timeline
                EventoTimeline.objects.create(
                    processo=processo,
                    titulo="Processo Criado",
                    descricao=f"Processo iniciado por {request.user.get_full_name() or request.user.username}.",
                    autor=request.user,
                    icone="bi-plus-circle-fill"
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
    """
    Exibe detalhes completos do processo e permite upload de anexos extras.
    Contém travas de segurança para visualização.
    """
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    # 1. Validação de Permissão de Visualização
    tem_permissao = False
    if user.funcao == 'Gestor':
        tem_permissao = True
    elif user.funcao == 'Vendedor' and processo.criado_por == user:
        tem_permissao = True
    elif user.funcao == 'Separador':
        # Separador vê se for dele ou se estiver livre
        if processo.responsavel_separacao == user or processo.responsavel_separacao is None:
            tem_permissao = True

    if not tem_permissao:
        raise PermissionDenied(
            "Você não tem permissão para visualizar este processo.")

    # 2. Processamento de Upload de Anexos
    if request.method == 'POST':
        # Segurança: Bloqueia edições em processos cancelados
        if processo.is_cancelado:
            messages.error(
                request, 'Não é possível anexar arquivos em processos cancelados.')
            return redirect('samples:detalhe_processo', pk=pk)

        if 'upload_anexos' in request.POST:
            form = AnexoForm(request.POST, request.FILES)
            if form.is_valid():
                arquivos = request.FILES.getlist('arquivo')
                if arquivos:
                    for f in arquivos:
                        Anexo.objects.create(processo=processo, arquivo=f)

                    EventoTimeline.objects.create(
                        processo=processo,
                        titulo="Anexos Adicionados",
                        descricao=f"{len(arquivos)} arquivo(s) adicionado(s).",
                        autor=request.user,
                        icone="bi-paperclip"
                    )
                    messages.success(
                        request, f'{len(arquivos)} arquivo(s) anexado(s)!')
                return redirect('samples:detalhe_processo', pk=pk)
    else:
        form = AnexoForm()

    context = {
        'processo': processo,
        'anexo_form': form,
    }
    return render(request, 'samples/detalhes-processo.html', context)


# ==============================================================================
# BLOCO 2: APIs PARA MODAIS E AÇÕES (AJAX)
# ==============================================================================

@login_required
@require_http_methods(["POST"])
def api_toggle_cancel_process(request, pk):
    """
    API para Cancelar ou Reativar um processo.
    Restrito a Gestores ou ao Criador do processo.
    """
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    if user.funcao != 'Gestor' and processo.criado_por != user:
        return JsonResponse({'status': 'error', 'message': 'Sem permissão.'}, status=403)

    try:
        if processo.status == 'cancelado':
            # Lógica de Reativação
            processo.status = 'nao_atribuido'
            processo.responsavel_separacao = None  # Retorna para a fila geral
            processo.save()

            EventoTimeline.objects.create(
                processo=processo,
                titulo="Processo Reativado",
                descricao=f"Reaberto por {user.get_full_name()}. Voltou para a fila geral.",
                autor=user,
                icone="bi-arrow-counterclockwise"
            )
            msg = "Processo reativado com sucesso!"
        else:
            # Lógica de Cancelamento
            processo.status = 'cancelado'
            # Mantemos o responsável (se houver) para histórico
            processo.save()

            EventoTimeline.objects.create(
                processo=processo,
                titulo="⛔ Processo Cancelado",
                descricao=f"Cancelado por {user.get_full_name()}.",
                autor=user,
                icone="bi-x-octagon-fill"
            )
            msg = "Processo cancelado."

        return JsonResponse({'status': 'success', 'message': msg})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_update_status(request, pk):
    """
    API para atualizar o status do processo.
    Implementa atribuição implícita: se não tiver dono, quem altera vira o dono.
    """
    if request.user.funcao != 'Separador':
        return JsonResponse({'status': 'error', 'message': 'Sem permissão.'}, status=403)

    try:
        processo = get_object_or_404(Processo, pk=pk)

        # Segurança: Processo cancelado é imutável
        if processo.is_cancelado:
            return JsonResponse({'status': 'error', 'message': 'Processo cancelado. Ação bloqueada.'}, status=400)

        # Regra: Não pode mexer no processo de outro separador
        if processo.responsavel_separacao and processo.responsavel_separacao != request.user:
            return JsonResponse({'status': 'error', 'message': 'Processo pertence a outro usuário.'}, status=403)

        # Regra: Atribuição Implícita (Quem mexe, assume)
        if not processo.responsavel_separacao:
            processo.responsavel_separacao = request.user
            EventoTimeline.objects.create(
                processo=processo,
                titulo="Processo Assumido",
                descricao=f"Ao alterar o status, {request.user.get_full_name()} assumiu a responsabilidade.",
                autor=request.user,
                icone="bi-person-check-fill"
            )

        data = json.loads(request.body)
        novo_status = data.get('status')
        status_antigo = processo.get_status_display()

        processo.status = novo_status
        processo.save()

        EventoTimeline.objects.create(
            processo=processo,
            titulo="Status Alterado",
            descricao=f"Mudou de '{status_antigo}' para '{processo.get_status_display()}'",
            autor=request.user,
            icone="bi-arrow-repeat"
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_update_rastreio(request, pk):
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    # 1. Verifica Permissões (Lógica Nova)
    is_separador = user.funcao == 'Separador'
    # Vendedor pode SE for o dono E for Carga
    is_vendedor_dono_carga = (
        processo.criado_por == user and
        processo.tipo_transporte == 'carga'
    )

    if not (is_separador or is_vendedor_dono_carga):
        return JsonResponse({'status': 'error', 'message': 'Sem permissão.'}, status=403)

    try:
        # 2. Verificações de Segurança Padrão
        if processo.is_cancelado:
            return JsonResponse({'status': 'error', 'message': 'Processo cancelado.'}, status=400)

        # Se for Separador, mantém a regra de propriedade (só mexe no seu)
        if is_separador and processo.responsavel_separacao and processo.responsavel_separacao != user:
            return JsonResponse({'status': 'error', 'message': 'Processo pertence a outro usuário.'}, status=403)

        # Auto-atribuição (Apenas para Separador)
        if is_separador and not processo.responsavel_separacao:
            processo.responsavel_separacao = user
            EventoTimeline.objects.create(
                processo=processo,
                titulo="Processo Assumido",
                autor=user,
                icone="bi-person-check-fill"
            )

        # 3. Atualização e Timeline
        data = json.loads(request.body)
        novo_codigo = data.get('codigo_rastreio')

        # Verifica se mudou para não poluir timeline
        if processo.codigo_rastreio != novo_codigo:
            processo.codigo_rastreio = novo_codigo
            processo.save()

            # Título diferente dependendo de quem alterou
            titulo_evento = "Código de Carga" if is_vendedor_dono_carga else "Código de Rastreio"

            EventoTimeline.objects.create(
                processo=processo,
                titulo=titulo_evento,
                descricao=f"Código definido/alterado para: {novo_codigo}",
                autor=user,
                icone="bi-truck"
            )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_add_comentario(request, pk):
    """
    API para adicionar comentários ou ocorrências.
    """
    try:
        processo = get_object_or_404(Processo, pk=pk)

        if processo.is_cancelado:
            return JsonResponse({'status': 'error', 'message': 'Processo cancelado.'}, status=400)

        data = json.loads(request.body)
        texto = data.get('texto')
        encaminhar = data.get('encaminhar_gestao', False)

        if not texto:
            return JsonResponse({'status': 'error', 'message': 'Texto vazio.'}, status=400)

        Comentario.objects.create(
            processo=processo,
            autor=request.user,
            texto=texto,
            encaminhar_gestao=encaminhar
        )

        if encaminhar:
            EventoTimeline.objects.create(
                processo=processo,
                titulo="⚠️ Ocorrência Reportada",
                descricao=f"Encaminhado para gestão: {texto[:50]}...",
                autor=request.user,
                icone="bi-exclamation-triangle-fill"
            )
        else:
            EventoTimeline.objects.create(
                processo=processo,
                titulo="Comentário Adicionado",
                autor=request.user,
                icone="bi-chat-left-text"
            )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_assign_process(request, pk):
    """
    API para atribuição manual ("Atribuir a mim").
    """
    if request.user.funcao != 'Separador':
        return JsonResponse({'status': 'error', 'message': 'Sem permissão.'}, status=403)

    try:
        processo = get_object_or_404(Processo, pk=pk)

        if processo.is_cancelado:
            return JsonResponse({'status': 'error', 'message': 'Não é possível assumir processos cancelados.'}, status=400)

        if processo.responsavel_separacao:
            return JsonResponse({'status': 'error', 'message': 'Este processo já tem um responsável.'}, status=400)

        processo.responsavel_separacao = request.user
        # Se estiver "Não Atribuído", avança para "Atribuído"
        if processo.status == 'nao_atribuido':
            processo.status = 'atribuido'

        processo.save()

        EventoTimeline.objects.create(
            processo=processo,
            titulo="Processo Atribuído",
            descricao=f"O colaborador {request.user.get_full_name() or request.user.username} assumiu a responsabilidade.",
            autor=request.user,
            icone="bi-person-check-fill"
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ==============================================================================
# BLOCO 3: APIs DE CLIENTES (BUSCA E EDIÇÃO)
# ==============================================================================

@login_required
def search_clientes_api(request):
    term = request.GET.get('term', '')
    # Pesquisa por nome ou responsável
    clientes = Cliente.objects.filter(
        Q(nome__icontains=term) | Q(responsavel__icontains=term)
    )[:10]

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
        cliente = Cliente.objects.create(
            nome=data.get('nome'), responsavel=data.get('responsavel'), cep=data.get('cep'),
            logradouro=data.get('logradouro'), numero=data.get('numero'),
            complemento=data.get('complemento'), bairro=data.get('bairro'),
            cidade=data.get('cidade'), estado=data.get('estado'),
        )
        return JsonResponse({
            'status': 'success',
            'cliente': {
                'id': cliente.id, 'nome': cliente.nome, 'responsavel': cliente.responsavel,
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

        # Snapshot para auditoria
        endereco_antigo = f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado} (CEP: {cliente.cep})"

        # Atualização
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

        endereco_novo = f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado} (CEP: {cliente.cep})"

        # Auditoria: Se endereço mudou, notifica nos processos ativos
        if endereco_antigo != endereco_novo:
            processos_afetados = Processo.objects.filter(cliente=cliente).exclude(
                status__in=['entregue', 'nao_entregue', 'cancelado']
            )
            for processo in processos_afetados:
                EventoTimeline.objects.create(
                    processo=processo,
                    titulo="⚠️ Dados do Cliente Alterados",
                    descricao=f"O endereço de entrega foi modificado.\n\nANTERIOR: {endereco_antigo}\nNOVO: {endereco_novo}\n\nAlterado por: {request.user.get_full_name()}",
                    autor=request.user,
                    icone="bi-geo-alt-fill"
                )

        return JsonResponse({
            'status': 'success',
            'cliente': {
                'id': cliente.id, 'nome': cliente.nome, 'responsavel': cliente.responsavel,
                'cep': cliente.cep, 'logradouro': cliente.logradouro,
                'numero': cliente.numero, 'complemento': cliente.complemento,
                'bairro': cliente.bairro, 'cidade': cliente.cidade,
                'estado': cliente.estado,
                'endereco_completo': f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}"
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ==============================================================================
# BLOCO 4: CRUD DE CLIENTES (VIEWS PADRÃO)
# ==============================================================================

@login_required
def cliente_list_view(request):
    query = request.GET.get('q')
    clientes_list = Cliente.objects.all().order_by('nome')
    if query:
        clientes_list = clientes_list.filter(
            Q(nome__icontains=query) |
            Q(responsavel__icontains=query) |
            Q(cidade__icontains=query)
        )
    paginator = Paginator(clientes_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'samples/lista-clientes.html', {'page_obj': page_obj, 'query': query})


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
    if request.user.funcao != 'Gestor':
        messages.error(request, 'Apenas gestores podem excluir clientes.')
        return redirect('samples:lista_clientes')
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=pk)
        try:
            cliente.delete()
            messages.success(request, 'Cliente excluído com sucesso.')
        except ProtectedError:
            messages.error(
                request, 'Não é possível excluir este cliente pois ele possui Processos vinculados.')
    return redirect('samples:lista_clientes')
