from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UsuarioCustomizado


class CustomUserCreationForm(forms.ModelForm):
    # Campo de senha para criação
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UsuarioCustomizado
        # Campos que aparecerão no formulário de CRIAÇÃO
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password', 'funcao', 'setor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes do Bootstrap a todos os campos
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(
                {'class': 'form-control'})

    def save(self, commit=True):
        # Sobrescreve o 'save' para hashear (criptografar) a senha
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    # Formulário para EDIÇÃO (não exige senha)
    class Meta:
        model = UsuarioCustomizado
        # Campos que aparecerão no formulário de EDIÇÃO
        fields = ('username', 'first_name', 'last_name',
                  'email', 'funcao', 'setor', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name == 'is_active':
                self.fields[field_name].widget.attrs.update(
                    {'class': 'form-check-input'})
            else:
                self.fields[field_name].widget.attrs.update(
                    {'class': 'form-control'})
