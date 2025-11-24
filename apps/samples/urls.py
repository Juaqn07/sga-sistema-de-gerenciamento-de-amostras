from django.urls import path
from . import views  # Importa as views do app

app_name = 'samples'

urlpatterns = [
    # URL: /processos/
    path('', views.process_list_view, name='lista_processos'),

    # URL: /processos/criar/
    path('criar/', views.process_create_view, name='criar_processo'),

    # URL: /processos/1/ (exemplo de detalhe)
    # O <int:pk> captura o ID do processo da URL
    path('<int:pk>/', views.process_detail_view, name='detalhe_processo'),

    path('api/buscar-clientes/', views.search_clientes_api,
         name='api_search_clientes'),
    path('api/criar-cliente/', views.create_cliente_api, name='api_create_cliente'),
    path('api/editar-cliente/<int:pk>/',
         views.edit_cliente_api, name='api_edit_cliente'),

    path('clientes/', views.cliente_list_view, name='lista_clientes'),
    path('clientes/criar/', views.cliente_create_view, name='criar_cliente'),
    path('clientes/<int:pk>/editar/',
         views.cliente_update_view, name='editar_cliente'),
    path('clientes/<int:pk>/deletar/',
         views.cliente_delete_view, name='deletar_cliente'),
]
