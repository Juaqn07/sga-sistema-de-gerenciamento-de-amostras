from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustomizado


class UsuarioCustomizadoAdmin(UserAdmin):
    """
    Configuração do Painel Admin para suportar o modelo de usuário customizado.
    Estende o UserAdmin padrão para incluir os campos 'funcao' e 'setor' nas telas de edição.
    """

    # Adiciona os campos customizados na tela de EDICÃO de usuário existente
    fieldsets = UserAdmin.fieldsets + (
        ('Campos Customizados', {'fields': ('funcao', 'setor')}),
    )

    # Adiciona os campos customizados na tela de CRIAÇÃO de novo usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Customizados', {'fields': ('funcao', 'setor')}),
    )


# Registra o modelo customizado
admin.site.register(UsuarioCustomizado, UsuarioCustomizadoAdmin)
