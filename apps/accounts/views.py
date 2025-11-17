from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
# Importa o formulário de login do Django
from django.contrib.auth.forms import AuthenticationForm
# Feedbacks
from django.contrib import messages
# Busca de usuários
from django.core.paginator import Paginator
from django.db.models import Q
# Importa nosso modelo de usuário
from .models import UsuarioCustomizado
# Formulário CRUD
from .forms import CustomUserCreationForm, CustomUserChangeForm


def login_view(request):
    # Se o usuário já estiver logado, redireciona para o dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        # 1. Processa os dados do formulário
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # 2. Pega os dados limpos
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # 3. Tenta autenticar
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # 4. Se o usuário for válido, loga ele
                login(request, user)
                # 5. Redireciona para o dashboard
                return redirect('dashboard:home')
            else:
                # (O formulário já vai conter o erro de "usuário/senha inválido")
                pass
    else:
        # Se for GET, apenas mostra um formulário em branco
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # Redireciona para a página de login


@login_required
def user_list_view(request):
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')
    # 1. LÓGICA DE BUSCA
    # Pega o termo de busca da URL (ex: ?q=nome)
    query = request.GET.get('q')

    # Começa com a lista de todos os usuários
    usuarios_list = UsuarioCustomizado.objects.filter(
        is_superuser=False).order_by('first_name')

    if query:
        # Se houver busca, filtra a lista
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    # 2. LÓGICA DE PAGINAÇÃO
    # Cria um Paginator com a lista (filtrada ou não), mostrando 10 usuários por pág.
    paginator = Paginator(usuarios_list, 10)

    # Pega o número da página da URL (ex: ?page=2)
    page_number = request.GET.get('page')

    # Pega os objetos daquela página específica
    page_obj = paginator.get_page(page_number)

    context = {
        # 3. ENVIA A PÁGINA (E A BUSCA) PARA O TEMPLATE
        'page_obj': page_obj,  # 'page_obj' contém os 10 usuários da página atual
        'query': query,        # Envia a busca de volta para preencher o formulário
    }
    return render(request, 'accounts/lista-usuarios.html', context)


@login_required
def user_create_view(request):
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

    context = {
        'form': form
    }
    return render(request, 'accounts/form-usuario.html', context)


@login_required
def user_edit_view(request, pk):
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    # Busca o usuário que queremos editar, ou dá erro 404
    usuario_para_editar = get_object_or_404(UsuarioCustomizado, pk=pk)

    if request.method == 'POST':
        # 'instance=usuario_para_editar' preenche o form com os dados do usuário
        form = CustomUserChangeForm(request.POST, instance=usuario_para_editar)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('accounts:lista_usuarios')
    else:
        # Se for GET, mostra o formulário preenchido
        form = CustomUserChangeForm(instance=usuario_para_editar)

    context = {
        'form': form
    }
    return render(request, 'accounts/form-usuario.html', context)


@login_required
def user_delete_view(request, pk):
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    # A deleção só deve ocorrer se o método for POST
    if request.method == 'POST':
        try:
            # Encontra o usuário
            usuario_para_deletar = get_object_or_404(UsuarioCustomizado, pk=pk)

            # Garante que o usuário não possa se auto-deletar
            if usuario_para_deletar.id == request.user.id:
                messages.error(request, 'Você não pode excluir a si mesmo.')
                return redirect('accounts:lista_usuarios')

            # Deleta o usuário do banco
            usuario_para_deletar.delete()
            messages.success(request, 'Usuário excluído com sucesso.')

        except UsuarioCustomizado.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            pass

    # Redireciona de volta para a lista (seja por POST ou GET)
    return redirect('accounts:lista_usuarios')


@login_required
def profile_view(request):
    user = request.user  # Pega o usuário logado

    if request.method == 'POST':
        # 1. Lógica para salvar os dados

        # Pega os dados do formulário
        nome_completo = request.POST.get('nome_completo')
        email = request.POST.get('email')

        # Separa o nome completo em primeiro e último nome
        if nome_completo:
            partes_nome = nome_completo.split(' ', 1)
            user.first_name = partes_nome[0]
            user.last_name = partes_nome[1] if len(partes_nome) > 1 else ''

        user.email = email

        # 2. Lógica para salvar a foto
        if 'foto_perfil' in request.FILES:
            user.foto = request.FILES['foto_perfil']

        # 3. Lógica para trocar senha
        nova_senha = request.POST.get('nova_senha')
        confirma_senha = request.POST.get('confirma_senha')

        if nova_senha:  # Verifica se o usuário quer mudar a senha
            if nova_senha == confirma_senha:
                # Usa set_password() para criptografar
                user.set_password(nova_senha)
                messages.success(
                    request, 'Sua senha foi alterada com sucesso!')
            else:
                messages.error(request, 'As novas senhas não conferem.')

        user.save()

        # 5. Atualiza a sessão do usuário para ele não ser deslogado
        if nova_senha:
            update_session_auth_hash(request, user)

        # Redireciona de volta para o perfil para mostrar as mudanças
        return redirect('accounts:perfil')

    # Se for GET, apenas mostra a página
    return render(request, 'accounts/perfil.html')
