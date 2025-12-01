from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuração principal da aplicação 'Accounts'.
    Gerencia autenticação, perfis de usuário e controle de acesso.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
