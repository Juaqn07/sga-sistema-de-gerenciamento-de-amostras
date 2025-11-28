from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UsuarioCustomizado


class CustomUserCreationForm(forms.ModelForm):
    # REQUISITO: Validação e Sanitização - Formulário com mais de 5 campos
    # O Django sanitiza automaticamente os dados nestes campos tipados

    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirmar Senha', widget=forms.PasswordInput)

    class Meta:
        model = UsuarioCustomizado
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password', 'confirm_password', 'funcao', 'setor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(
                {'class': 'form-control'})

    def clean(self):
        # REQUISITO: Filtro de Validação
        # Este método valida se as senhas conferem, atuando como um filtro lógico

        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não conferem.")

        return cleaned_data

    def save(self, commit=True):
        # REQUISITO: Criptografia de Senha
        # O método set_password aplica o hash PBKDF2/SHA256 antes de salvar no banco

        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Criptografa a senha
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    # Campos de redefinição de senha (OPCIONAIS)
    password = forms.CharField(
        label='Nova Senha (Opcional)', widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(
        label='Confirmar Nova Senha', widget=forms.PasswordInput, required=False)

    class Meta:
        model = UsuarioCustomizado
        fields = ('username', 'first_name', 'last_name',
                  'email', 'funcao', 'setor', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name == 'is_active':
                self.fields[field_name].widget.attrs.update(
                    {'class': 'form-check-input'})
            elif field_name in ('password', 'confirm_password'):
                self.fields[field_name].widget.attrs.update(
                    {'class': 'form-control', 'placeholder': 'Deixe em branco para não alterar'})
            else:
                self.fields[field_name].widget.attrs.update(
                    {'class': 'form-control'})

    def clean(self):
        # Validação para ver se as senhas batem (se foram preenchidas)
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não conferem.")

        return cleaned_data

    def save(self, commit=True):
        # Salva o usuário normal
        user = super().save(commit=False)

        # Se o campo de senha foi preenchido, atualiza a senha
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)  # Criptografa

        if commit:
            user.save()
        return user
