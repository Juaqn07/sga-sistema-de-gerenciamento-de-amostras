from django.urls import path
from . import views

# Namespace para referenciar urls no template: {% url 'dashboard:home' %}
app_name = 'dashboard'

urlpatterns = [
    # Rota Principal (Dashboard)
    # Acessível em: /dashboard/ (configurado no urls.py raiz do projeto)
    path('', views.dashboard_view, name='home'),
]
