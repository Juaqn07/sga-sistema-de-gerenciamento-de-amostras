from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='perfil'),

    # /usuarios/ (A nova lista de usuários)
    path('usuarios/', views.user_list_view, name='lista_usuarios'),

    # /usuarios/criar/ (O formulário de criação)
    path('usuarios/criar/', views.user_create_view, name='criar_usuario'),

    # /usuarios/1/editar/ (O formulário de edição)
    path('usuarios/<int:pk>/editar/', views.user_edit_view, name='editar_usuario'),

    # /usuarios/1/deletar/ (A ação de deletar)
    path('usuarios/<int:pk>/deletar/',
         views.user_delete_view, name='deletar_usuario'),
]
