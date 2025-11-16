from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# Importa o formulário de login do Django
from django.contrib.auth.forms import AuthenticationForm
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

# ---
# PROTEÇÃO DAS OUTRAS VIEWS
# ---


@login_required
def user_list_view(request):  # ANTIGA register_user_view
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    usuarios = UsuarioCustomizado.objects.filter(
        is_superuser=False).order_by('first_name')
    context = {
        'usuarios_cadastrados': usuarios
    }
    # Aponta para o NOVO template de lista
    return render(request, 'accounts/lista-usuarios.html', context)


@login_required
def user_create_view(request):
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # (Mensagem de sucesso pode ser adicionada aqui depois)
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
                # (Aqui poderíamos adicionar uma msg de erro)
                return redirect('accounts:lista_usuarios')

            # Deleta o usuário do banco
            usuario_para_deletar.delete()
            # (Aqui poderíamos adicionar uma msg de sucesso)

        except UsuarioCustomizado.DoesNotExist:
            # (Aqui poderíamos adicionar uma msg de erro)
            pass

    # Redireciona de volta para a lista (seja por POST ou GET)
    return redirect('accounts:lista_usuarios')


@login_required  # Garante que só usuários logados vejam
def profile_view(request):
    return render(request, 'accounts/perfil.html')


def password_recovery_view(request):
    return render(request, 'accounts/recuperar-senha.html')
