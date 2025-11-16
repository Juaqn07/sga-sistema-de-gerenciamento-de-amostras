from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustomizado

# Define um "admin model" customizado


class UsuarioCustomizadoAdmin(UserAdmin):
    # O 'fieldsets' padrão do UserAdmin, mais os nossos campos
    fieldsets = UserAdmin.fieldsets + (
        # Adiciona 'setor' junto com 'funcao'
        ('Campos Customizados', {'fields': ('funcao', 'setor')}),
    )  # type: ignore
    # O 'add_fieldsets' é para a tela de *criação* de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Customizados', {'fields': ('funcao', 'setor')}),
    )  # type: ignore


# Registra o nosso modelo customizado com a nossa classe customizada
admin.site.register(UsuarioCustomizado, UsuarioCustomizadoAdmin)
