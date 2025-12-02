from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import UsuarioCustomizado
from .forms import CustomUserCreationForm, CustomUserChangeForm

# ==============================================================================
# 1. AUTENTICAÇÃO (LOGIN / LOGOUT)
# ==============================================================================


def login_view(request):
    """
    Gerencia o processo de login do usuário.

    REQUISITO: Efetuar Login e Sessão.
    Autentica credenciais contra o banco de dados (hash) e cria a sessão segura.
    """
    # Se já logado, não precisa ver tela de login
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        # 1. Validação do formulário padrão do Django
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # 2. Extração de credenciais limpas
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # 3. Autenticação (Verifica hash da senha)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # 4. Criação da Sessão (Login efetivo)
                login(request, user)
                return redirect('dashboard:home')

            # Caso authenticate falhe (ex: usuário inativo), o form gerará erro na próxima renderização
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Encerra a sessão do usuário e redireciona para login."""
    logout(request)
    return redirect('accounts:login')


# ==============================================================================
# 2. GESTÃO DE PERFIL (PRÓPRIO USUÁRIO)
# ==============================================================================

@login_required
def profile_view(request):
    """
    Permite ao usuário logado editar seus próprios dados básicos e senha.
    Inclui lógica manual para troca de senha e atualização de hash de sessão.
    """
    user = request.user

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'remover_foto':
            if user.foto:
                user.foto.delete(save=False)  # Remove o arquivo físico
                user.foto = None             # Limpa a referência no banco
                user.save()
                messages.success(
                    request, 'Foto de perfil removida com sucesso.')
            return redirect('accounts:perfil')
        else:
            # --- 1. Atualização de Dados Cadastrais ---
            nome_completo = request.POST.get('nome_completo')
            email = request.POST.get('email')

            # Lógica para separar Nome e Sobrenome
            if nome_completo:
                partes_nome = nome_completo.split(' ', 1)
                user.first_name = partes_nome[0]
                user.last_name = partes_nome[1] if len(partes_nome) > 1 else ''

            user.email = email

            # --- 2. Upload de Foto ---
            if 'foto_perfil' in request.FILES:
                user.foto = request.FILES['foto_perfil']

            # --- 3. Troca de Senha Manual ---
            nova_senha = request.POST.get('nova_senha')
            confirma_senha = request.POST.get('confirma_senha')

            if nova_senha:
                if nova_senha == confirma_senha:
                    # Aplica criptografia na nova senha
                    user.set_password(nova_senha)
                    messages.success(
                        request, 'Sua senha foi alterada com sucesso!')

                    # REQUISITO CRÍTICO: Atualizar hash da sessão
                    # Sem isso, o usuário seria deslogado automaticamente após mudar a senha
                    update_session_auth_hash(request, user)
                else:
                    messages.error(request, 'As novas senhas não conferem.')

            user.save()
            return redirect('accounts:perfil')

    return render(request, 'accounts/perfil.html')


# ==============================================================================
# 3. GESTÃO DE USUÁRIOS (CRUD - APENAS GESTOR)
# ==============================================================================

@login_required
def user_list_view(request):
    """
    Lista usuários do sistema com filtro de busca e paginação.
    Acesso restrito a usuários com função 'Gestor'.
    """
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    # --- 1. Filtros de Busca ---
    query = request.GET.get('q')
    usuarios_list = UsuarioCustomizado.objects.filter(
        is_superuser=False).order_by('first_name')

    if query:
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    # --- 2. Paginação ---
    paginator = Paginator(usuarios_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'accounts/lista-usuarios.html', context)


@login_required
def user_create_view(request):
    """
    Cria um novo usuário no sistema.
    Acesso restrito a Gestores.
    """
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('accounts:lista_usuarios')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/form-usuario.html', {'form': form})


@login_required
def user_edit_view(request, pk):
    """
    Edita um usuário existente.
    Acesso restrito a Gestores.
    """
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    usuario_para_editar = get_object_or_404(UsuarioCustomizado, pk=pk)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=usuario_para_editar)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('accounts:lista_usuarios')
    else:
        form = CustomUserChangeForm(instance=usuario_para_editar)

    return render(request, 'accounts/form-usuario.html', {'form': form})


@login_required
def user_delete_view(request, pk):
    """
    Inativa (Soft Delete) um usuário.
    Não exclui fisicamente do banco para manter integridade histórica.
    """
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    if request.method == 'POST':
        try:
            usuario_para_inativar = get_object_or_404(
                UsuarioCustomizado, pk=pk)

            # Proteção: Usuário não pode inativar a si mesmo
            if usuario_para_inativar.id == request.user.id:
                messages.error(request, 'Você não pode inativar a si mesmo.')
                return redirect('accounts:lista_usuarios')

            usuario_para_inativar.is_active = False
            usuario_para_inativar.save()
            messages.success(request, 'Usuário inativado com sucesso.')

        except UsuarioCustomizado.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    return redirect('accounts:lista_usuarios')
