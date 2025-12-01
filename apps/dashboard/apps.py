from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """
    Configuração do app 'Dashboard'.
    Responsável pela visão gerencial, agregação de KPIs e gráficos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'
