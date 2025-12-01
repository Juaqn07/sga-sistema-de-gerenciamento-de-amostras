from django import forms
from .models import UsuarioCustomizado


class CustomUserCreationForm(forms.ModelForm):
    """
    Formulário para CRIAÇÃO de novos usuários (Gestão).

    REQUISITOS ATENDIDOS:
    1. Validação e Sanitização (Clean method).
    2. Criptografia de Senha (Save method).
    """

    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirmar Senha', widget=forms.PasswordInput)

    class Meta:
        model = UsuarioCustomizado
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password', 'confirm_password', 'funcao', 'setor')

    def __init__(self, *args, **kwargs):
        """Inicializa o form aplicando classes Bootstrap em todos os campos."""
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(
                {'class': 'form-control'})

    def clean(self):
        """
        REQUISITO: Filtro de Validação
        Valida se os campos de senha e confirmação de senha são idênticos.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não conferem.")

        return cleaned_data

    def save(self, commit=True):
        """
        REQUISITO: Criptografia de Senha
        Intercepta o salvamento para aplicar o hash (PBKDF2) na senha antes de ir ao banco.
        """
        user = super().save(commit=False)

        # O método set_password faz o hash seguro
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    Formulário para EDIÇÃO de usuários existentes.
    Permite alteração de dados cadastrais e troca opcional de senha.
    """

    # Campos de senha são opcionais na edição
    password = forms.CharField(
        label='Nova Senha (Opcional)', widget=forms.PasswordInput, required=False
    )
    confirm_password = forms.CharField(
        label='Confirmar Nova Senha', widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = UsuarioCustomizado
        fields = ('username', 'first_name', 'last_name',
                  'email', 'funcao', 'setor', 'is_active')

    def __init__(self, *args, **kwargs):
        """Configura widgets e placeholders para edição."""
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            widget = self.fields[field_name].widget

            # Checkbox tem classe diferente no Bootstrap
            if field_name == 'is_active':
                widget.attrs.update({'class': 'form-check-input'})
            # Campos de senha recebem placeholder explicativo
            elif field_name in ('password', 'confirm_password'):
                widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Deixe em branco para não alterar'
                })
            else:
                widget.attrs.update({'class': 'form-control'})

    def clean(self):
        """Valida igualdade de senhas apenas se o usuário tentou alterá-las."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não conferem.")

        return cleaned_data

    def save(self, commit=True):
        """Salva alterações, atualizando a senha apenas se fornecida."""
        user = super().save(commit=False)

        # Verifica se houve entrada de nova senha
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user
