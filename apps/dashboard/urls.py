from django.urls import path
from . import views  # Importa as views do app

app_name = 'dashboard'  # Para o {% url 'dashboard:home' %}

urlpatterns = [
    # URL: /dashboard/
    # O prefixo 'dashboard/' já estará no urls.py principal
    path('', views.dashboard_view, name='home'),
]
