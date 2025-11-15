from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustomizado

# Define um "admin model" customizado


class UsuarioCustomizadoAdmin(UserAdmin):
    # O 'fieldsets' padrão do UserAdmin, mais o nosso campo 'funcao'
    fieldsets = UserAdmin.fieldsets + \
        (('Campos Customizados', {'fields': ('funcao',)}),)  # type: ignore
    # O 'add_fieldsets' é para a tela de *criação* de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Customizados', {'fields': ('funcao',)}),
    )  # type: ignore


# Registra o nosso modelo customizado com a nossa classe customizada
admin.site.register(UsuarioCustomizado, UsuarioCustomizadoAdmin)
