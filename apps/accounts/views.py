from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# Importa o formulário de login do Django
from django.contrib.auth.forms import AuthenticationForm

# ---
# NOVA LÓGICA DE LOGIN
# ---


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

# ---
# NOVA LÓGICA DE LOGOUT
# ---


def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # Redireciona para a página de login

# ---
# PROTEÇÃO DAS OUTRAS VIEWS
# ---


@login_required  # Garante que só usuários logados vejam
def register_user_view(request):
    if request.user.funcao != 'Gestor':
        return redirect('dashboard:home')

    context = {
        'usuarios_cadastrados': []  # (Lógica de cadastro virá depois)
    }
    return render(request, 'accounts/cadastrar-usuario.html', context)


@login_required  # Garante que só usuários logados vejam
def profile_view(request):
    return render(request, 'accounts/perfil.html')


def password_recovery_view(request):
    return render(request, 'accounts/recuperar-senha.html')
