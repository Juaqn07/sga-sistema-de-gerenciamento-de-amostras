from django.urls import path
from . import views  # Importa as views do app

app_name = 'samples'  # Essencial para o {% url 'samples:lista' %}

urlpatterns = [
    # URL: /processos/
    path('', views.process_list_view, name='lista_processos'),

    # URL: /processos/criar/
    path('criar/', views.process_create_view, name='criar_processo'),

    # URL: /processos/1/ (exemplo de detalhe)
    # O <int:pk> captura o ID do processo da URL
    path('<int:pk>/', views.process_detail_view, name='detalhe_processo'),
]
