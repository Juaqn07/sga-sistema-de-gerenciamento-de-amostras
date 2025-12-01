from django.urls import path
from . import views

app_name = 'samples'

urlpatterns = [
    # ==========================================
    # 1. PROCESSOS (CRUD & VISUALIZAÇÃO)
    # ==========================================
    path('', views.process_list_view, name='lista_processos'),
    path('criar/', views.process_create_view, name='criar_processo'),
    path('<int:pk>/', views.process_detail_view, name='detalhe_processo'),

    # ==========================================
    # 2. CLIENTES (CRUD & VISUALIZAÇÃO)
    # ==========================================
    path('clientes/', views.cliente_list_view, name='lista_clientes'),
    path('clientes/criar/', views.cliente_create_view, name='criar_cliente'),
    path('clientes/<int:pk>/editar/',
         views.cliente_update_view, name='editar_cliente'),
    path('clientes/<int:pk>/deletar/',
         views.cliente_delete_view, name='deletar_cliente'),

    # ==========================================
    # 3. APIs INTERNAS (AJAX / JSON)
    # ==========================================

    # APIs de Processo
    path('api/processo/<int:pk>/status/',
         views.api_update_status, name='api_update_status'),
    path('api/processo/<int:pk>/rastreio/',
         views.api_update_rastreio, name='api_update_rastreio'),
    path('api/processo/<int:pk>/comentario/',
         views.api_add_comentario, name='api_add_comentario'),
    path('api/processo/<int:pk>/atribuir/',
         views.api_assign_process, name='api_assign_process'),
    path('api/processo/<int:pk>/cancelar/',
         views.api_toggle_cancel_process, name='api_toggle_cancel'),

    # APIs de Cliente (Busca e Modal)
    path('api/buscar-clientes/', views.search_clientes_api,
         name='api_search_clientes'),
    path('api/criar-cliente/', views.create_cliente_api, name='api_create_cliente'),
    path('api/editar-cliente/<int:pk>/',
         views.edit_cliente_api, name='api_edit_cliente'),
]
