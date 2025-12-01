from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, ProtectedError
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
    """
    Exibe o Dashboard de Processos com filtros e regras de visualização por perfil.

    Regras de Negócio:
    - Vendedor: Vê apenas os processos que criou.
    - Separador: Vê processos atribuídos a ele ou "Não Atribuídos" (livres).
    - Gestor: Vê todos os processos.
    """
    user = request.user

    # --- 1. DEFINIÇÃO DO QUERYSET BASE (PERMISSÕES) ---
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

    # --- 2. APLICAÇÃO DE FILTROS (GET) ---
    query_term = request.GET.get('q')
    status_filter = request.GET.get('status')
    prioridade_filter = request.GET.get('prioridade')

    if query_term:
        base_qs = base_qs.filter(
            Q(codigo__icontains=query_term) |
            Q(titulo__icontains=query_term) |
            Q(codigo_rastreio__icontains=query_term) |
            Q(cliente__nome__icontains=query_term)
        )
    if status_filter:
        base_qs = base_qs.filter(status=status_filter)
    if prioridade_filter:
        base_qs = base_qs.filter(prioridade=prioridade_filter)

    # Ordenação padrão: Mais recentes primeiro
    base_qs = base_qs.order_by('-data_criacao')

    # --- 3. SEPARAÇÃO ESPECIAL PARA GESTOR ---
    # O Gestor vê uma lista separada ("Meus Processos") e "Todos os Processos"
    meus_processos_page_obj = None

    if user.funcao == 'Gestor':
        # Filtra processos onde o gestor atua diretamente
        meus_qs = base_qs.filter(
            Q(criado_por=user) | Q(responsavel_separacao=user)
        )
        # Remove "Meus Processos" da lista geral para não duplicar visualmente
        processos_qs = base_qs.exclude(id__in=meus_qs.values('id'))

        # Paginação exclusiva para "Meus Processos"
        mp_paginator = Paginator(meus_qs, 5)
        meus_processos_page_obj = mp_paginator.get_page(
            request.GET.get('mp_page'))
    else:
        processos_qs = base_qs

    # --- 4. PAGINAÇÃO DA LISTA PRINCIPAL ---
    paginator = Paginator(processos_qs, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Cálculo do total real para exibição
    total_count = paginator.count
    if meus_processos_page_obj:
        total_count += meus_processos_page_obj.paginator.count

    context = {
        'meus_processos': meus_processos_page_obj,
        'page_obj': page_obj,
        'total_processos': total_count,
        'status_choices': Processo.STATUS_CHOICES,
        'prioridade_choices': Processo.PRIORIDADE_CHOICES,
    }
    return render(request, 'samples/processos-do-setor.html', context)


@login_required
def process_create_view(request):
    """
    Gerencia a criação de processos.

    Fluxo:
    1. Recebe dados do formulário de processo.
    2. Recebe o ID do cliente selecionado (via campo oculto preenchido por AJAX).
    3. Salva o processo, vincula cliente e usuário criador.
    4. Cria registros iniciais (Anexo e Timeline).
    """
    if request.user.funcao == 'Separador':
        messages.error(request, 'Você não tem permissão para criar processos.')
        return redirect('samples:lista_processos')

    if request.method == 'POST':
        processo_form = ProcessoForm(request.POST, request.FILES)

        # O ID do cliente vem de um input oculto no template ('selected_cliente_id')
        cliente_id = request.POST.get('selected_cliente_id')

        if not cliente_id:
            messages.error(
                request, 'Por favor, selecione ou cadastre um destinatário.')
        elif processo_form.is_valid():
            try:
                cliente = Cliente.objects.get(id=cliente_id)

                # commit=False permite injetar dados antes de salvar no banco
                processo = processo_form.save(commit=False)
                processo.cliente = cliente
                processo.criado_por = request.user
                processo.status = 'nao_atribuido'
                processo.save()

                # Salva o relacionamento ManyToMany (Tipos de Amostra)
                processo_form.save_m2m()

                # Se houver anexo inicial (Pedido), cria o registro
                arquivo_enviado = processo_form.cleaned_data.get(
                    'arquivo_pedido')
                if arquivo_enviado:
                    Anexo.objects.create(
                        processo=processo, arquivo=arquivo_enviado)

                # Cria o primeiro evento na Timeline
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
                    request, 'Erro crítico: O cliente selecionado não foi encontrado no banco.')
    else:
        processo_form = ProcessoForm()

    return render(request, 'samples/criar-processo.html', {'processo_form': processo_form})


@login_required
def process_detail_view(request, pk):
    """
    Exibe detalhes completos do processo e permite upload de novos anexos.
    Inclui validação rigorosa de visualização baseada na função do usuário.
    """
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    # --- 1. VALIDAÇÃO DE PERMISSÃO DE VISUALIZAÇÃO ---
    tem_permissao = False
    if user.funcao == 'Gestor':
        tem_permissao = True
    elif user.funcao == 'Vendedor' and processo.criado_por == user:
        tem_permissao = True
    elif user.funcao == 'Separador':
        # Separador vê se for dele ou se estiver livre (para poder assumir)
        if processo.responsavel_separacao == user or processo.responsavel_separacao is None:
            tem_permissao = True

    if not tem_permissao:
        raise PermissionDenied(
            "Você não tem permissão para visualizar este processo.")

    # --- 2. LÓGICA DE UPLOAD DE ANEXOS ---
    if request.method == 'POST' and 'upload_anexos' in request.POST:
        if processo.is_cancelado:
            messages.error(
                request, 'Não é possível anexar arquivos em processos cancelados.')
            return redirect('samples:detalhe_processo', pk=pk)

        form = AnexoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivos = request.FILES.getlist(
                'arquivo')  # Suporta múltiplos arquivos
            if arquivos:
                for f in arquivos:
                    Anexo.objects.create(processo=processo, arquivo=f)

                # Registra na Timeline
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
# BLOCO 2: APIs PARA AÇÕES DE PROCESSO (USO VIA AJAX)
# ==============================================================================

@login_required
@require_http_methods(["POST"])
def api_toggle_cancel_process(request, pk):
    """
    API para Cancelar ou Reativar um processo.
    Restrição: Apenas Gestores ou o Criador (Vendedor) podem executar.
    """
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    if user.funcao != 'Gestor' and processo.criado_por != user:
        return JsonResponse({'status': 'error', 'message': 'Sem permissão.'}, status=403)

    try:
        if processo.status == 'cancelado':
            # --- LÓGICA DE REATIVAÇÃO ---
            processo.status = 'nao_atribuido'
            processo.responsavel_separacao = None  # Reseta a responsabilidade
            processo.save()

            EventoTimeline.objects.create(
                processo=processo,
                titulo="Processo Reativado",
                descricao=f"Reaberto por {user.get_full_name()}. Voltou para a fila geral.",
                autor=user,
                icone="bi-arrow-counterclockwise"
            )
            return JsonResponse({'status': 'success', 'message': "Processo reativado com sucesso!"})
        else:
            # --- LÓGICA DE CANCELAMENTO ---
            processo.status = 'cancelado'
            processo.save()

            EventoTimeline.objects.create(
                processo=processo,
                titulo="⛔ Processo Cancelado",
                descricao=f"Cancelado por {user.get_full_name()}.",
                autor=user,
                icone="bi-x-octagon-fill"
            )
            return JsonResponse({'status': 'success', 'message': "Processo cancelado."})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_update_status(request, pk):
    """
    API para atualização de Status via Modal.
    Implementa a 'Atribuição Implícita': Se um processo sem dono for modificado,
    o usuário atual se torna o responsável.
    """
    if request.user.funcao != 'Separador':
        return JsonResponse({'status': 'error', 'message': 'Apenas separadores alteram status.'}, status=403)

    try:
        processo = get_object_or_404(Processo, pk=pk)

        if processo.is_cancelado:
            return JsonResponse({'status': 'error', 'message': 'Processo cancelado.'}, status=400)

        # Regra de Propriedade
        if processo.responsavel_separacao and processo.responsavel_separacao != request.user:
            return JsonResponse({'status': 'error', 'message': 'Processo pertence a outro usuário.'}, status=403)

        # Regra de Atribuição Implícita
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
    """
    API para atualizar Código de Rastreio ou Carga.
    Permite que o Vendedor altere se for Carga e ele for o dono.
    """
    processo = get_object_or_404(Processo, pk=pk)
    user = request.user

    # --- Permissões Complexas ---
    is_separador = user.funcao == 'Separador'
    is_dono_carga = (processo.criado_por ==
                     user and processo.tipo_transporte == 'carga')

    if not (is_separador or is_dono_carga):
        return JsonResponse({'status': 'error', 'message': 'Sem permissão para alterar rastreio.'}, status=403)

    try:
        data = json.loads(request.body)
        novo_codigo = data.get('codigo_rastreio')

        if processo.codigo_rastreio != novo_codigo:
            processo.codigo_rastreio = novo_codigo
            processo.save()

            titulo_evento = "Código de Carga" if is_dono_carga else "Código de Rastreio"

            EventoTimeline.objects.create(
                processo=processo,
                titulo=titulo_evento,
                descricao=f"Código definido para: {novo_codigo}",
                autor=user,
                icone="bi-truck"
            )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_add_comentario(request, pk):
    """Adiciona um comentário simples ou uma ocorrência (flag de gestão)."""
    try:
        processo = get_object_or_404(Processo, pk=pk)
        data = json.loads(request.body)

        texto = data.get('texto')
        encaminhar = data.get('encaminhar_gestao', False)

        if not texto:
            return JsonResponse({'status': 'error', 'message': 'Texto vazio.'}, status=400)

        Comentario.objects.create(
            processo=processo, autor=request.user,
            texto=texto, encaminhar_gestao=encaminhar
        )

        # Log diferente na timeline dependendo da gravidade
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
    """Permite ao Separador atribuir um processo a si mesmo manualmente."""
    if request.user.funcao != 'Separador':
        return JsonResponse({'status': 'error', 'message': 'Ação exclusiva para Separadores.'}, status=403)

    try:
        processo = get_object_or_404(Processo, pk=pk)

        if processo.responsavel_separacao:
            return JsonResponse({'status': 'error', 'message': 'Este processo já tem responsável.'}, status=400)

        processo.responsavel_separacao = request.user
        if processo.status == 'nao_atribuido':
            processo.status = 'atribuido'
        processo.save()

        EventoTimeline.objects.create(
            processo=processo,
            titulo="Processo Atribuído",
            descricao=f"Colaborador {request.user.get_full_name()} assumiu a tarefa.",
            autor=request.user,
            icone="bi-person-check-fill"
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ==============================================================================
# BLOCO 3: APIs DE CLIENTES E VIEWS CRUD
# ==============================================================================

@login_required
def search_clientes_api(request):
    """
    API de Autocomplete para busca de clientes.
    Retorna JSON compatível com o frontend (criar-processo.js).
    """
    term = request.GET.get('term', '')
    if len(term) < 2:
        return JsonResponse({'results': []})

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
            'cep': c.cep,
            'bairro': c.bairro,
            'complemento': c.complemento,
            'endereco_completo': f"{c.logradouro}, {c.numero} - {c.cidade}/{c.estado}"
        })

    return JsonResponse({'results': results})


@login_required
@require_http_methods(["POST"])
def create_cliente_api(request):
    """Cria cliente via Modal (AJAX) sem recarregar a página."""
    try:
        data = json.loads(request.body)

        # Validação simples
        required_fields = ['nome', 'responsavel',
                           'logradouro', 'bairro', 'cidade', 'estado']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return JsonResponse({'status': 'error', 'message': f'Faltando: {", ".join(missing)}'}, status=400)

        cliente = Cliente.objects.create(
            nome=data.get('nome'),
            responsavel=data.get('responsavel'),
            cep=data.get('cep'),
            logradouro=data.get('logradouro'),
            numero=data.get('numero', 'S/N'),
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
                'endereco_completo': f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}",
                'cep': cliente.cep,
                # Retorna todos os campos para preencher o objeto JS
                'logradouro': cliente.logradouro, 'numero': cliente.numero,
                'bairro': cliente.bairro, 'cidade': cliente.cidade,
                'estado': cliente.estado, 'complemento': cliente.complemento
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def edit_cliente_api(request, pk):
    """Edita cliente e audita mudanças de endereço na timeline dos processos afetados."""
    try:
        cliente = get_object_or_404(Cliente, pk=pk)
        data = json.loads(request.body)

        old_address = f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}"

        # Atualiza campos
        cliente.nome = data.get('nome', cliente.nome)
        cliente.responsavel = data.get('responsavel', cliente.responsavel)
        cliente.cep = data.get('cep', cliente.cep)
        cliente.logradouro = data.get('logradouro', cliente.logradouro)
        cliente.numero = data.get('numero', cliente.numero)
        cliente.complemento = data.get('complemento', cliente.complemento)
        cliente.bairro = data.get('bairro', cliente.bairro)
        cliente.cidade = data.get('cidade', cliente.cidade)
        cliente.estado = data.get('estado', cliente.estado)
        cliente.save()

        new_address = f"{cliente.logradouro}, {cliente.numero} - {cliente.cidade}/{cliente.estado}"

        # Auditoria: Se endereço mudou, avisa nos processos em andamento
        if old_address != new_address:
            active_processes = Processo.objects.filter(cliente=cliente).exclude(
                status__in=['entregue', 'nao_entregue', 'cancelado']
            )
            for p in active_processes:
                EventoTimeline.objects.create(
                    processo=p,
                    titulo="⚠️ Dados do Cliente Alterados",
                    descricao=f"Endereço alterado.\nAntigo: {old_address}\nNovo: {new_address}\nPor: {request.user.get_full_name()}",
                    autor=request.user,
                    icone="bi-geo-alt-fill"
                )

        return JsonResponse({
            'status': 'success',
            'cliente': {
                'id': cliente.id, 'nome': cliente.nome, 'responsavel': cliente.responsavel,
                'endereco_completo': new_address, 'cep': cliente.cep,
                'logradouro': cliente.logradouro, 'numero': cliente.numero,
                'bairro': cliente.bairro, 'cidade': cliente.cidade,
                'estado': cliente.estado, 'complemento': cliente.complemento
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# --- VIEWS CLÁSSICAS DE CLIENTES (LISTAGEM/EDIÇÃO FORM PÁGINA) ---

@login_required
def cliente_list_view(request):
    """Listagem paginada de clientes."""
    query = request.GET.get('q')
    clientes_list = Cliente.objects.all().order_by('nome')

    if query:
        clientes_list = clientes_list.filter(
            Q(nome__icontains=query) | Q(responsavel__icontains=query)
        )

    paginator = Paginator(clientes_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'samples/lista-clientes.html', {'page_obj': page_obj, 'query': query})


@login_required
def cliente_create_view(request):
    """View padrão para criar cliente (fora do fluxo de processo)."""
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
    """View padrão para editar cliente."""
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
    """Exclusão de cliente com proteção de integridade referencial."""
    if request.user.funcao != 'Gestor':
        messages.error(request, 'Apenas gestores podem excluir clientes.')
        return redirect('samples:lista_clientes')

    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=pk)
        try:
            cliente.delete()
            messages.success(request, 'Cliente excluído.')
        except ProtectedError:
            messages.error(
                request, 'Impossível excluir: Cliente possui processos vinculados.')

    return redirect('samples:lista_clientes')
