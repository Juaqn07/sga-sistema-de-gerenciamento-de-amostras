from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração do app 'Core'.

    Este app atua como a infraestrutura base do projeto, contendo:
    1. Templates globais (como 'base.html').
    2. Arquivos estáticos compartilhados (CSS de layout, logotipos).
    3. Utilitários genéricos reutilizáveis por outros apps.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
