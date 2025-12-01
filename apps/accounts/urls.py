from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==========================================
    # 1. AUTENTICAÇÃO E PERFIL
    # ==========================================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='perfil'),

    # ==========================================
    # 2. GESTÃO DE USUÁRIOS (CRUD)
    # ==========================================
    # Listagem
    path('usuarios/', views.user_list_view, name='lista_usuarios'),

    # Criação
    path('usuarios/criar/', views.user_create_view, name='criar_usuario'),

    # Edição
    path('usuarios/<int:pk>/editar/', views.user_edit_view, name='editar_usuario'),

    # Exclusão (Soft Delete / Inativação)
    path('usuarios/<int:pk>/deletar/',
         views.user_delete_view, name='deletar_usuario'),
]
